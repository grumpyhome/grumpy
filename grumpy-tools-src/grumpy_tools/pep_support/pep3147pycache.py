# coding: utf-8


import os
import sys
import logging
import hashlib
import tempfile
import warnings
from backports.functools_lru_cache import lru_cache
from backports.tempfile import TemporaryDirectory

import importlib2
import grumpy_tools

from ..compiler import imputil

logger = logging.getLogger(__name__)

GOPATH_FOLDER = 'gopath'
TRANSPILED_MODULES_FOLDER = 'src/__python__/'
GRUMPY_MAGIC_TAG = 'grumpy-' + grumpy_tools.__version__.replace('.', '')  # alike cpython-27
ORIGINAL_MAGIC_TAG = sys.implementation.cache_tag  # On Py27, only because importlib2

_temporary_directories = []  # Will be cleaned up on main Python exit.


class SilentTemporaryDirectory(TemporaryDirectory):
    '''TemporaryDirectory that does not warn on implicit cleanup'''
    @classmethod
    def _cleanup(cls, name, warn_message):
        logger.debug(warn_message)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = TemporaryDirectory._cleanup(name, warn_message)
        return result


def get_depends_path(script_path, module_name):
    pycache_folder = get_pycache_folder(script_path, module_name)
    return os.path.join(pycache_folder, 'dependencies-%s.pkl' % module_name)


def get_checksum_path(script_path, module_name):
    pycache_folder = get_pycache_folder(script_path, module_name)
    return os.path.join(pycache_folder, 'checksum-%s.sha1' % module_name)


def get_checksum(stream):
    stream.seek(0)
    return hashlib.sha1(stream.read()).hexdigest()


def set_checksum(stream, script_path, module_name):
    with open(get_checksum_path(script_path, module_name), 'w') as chk_file:
        chk_file.write(get_checksum(stream))


def should_refresh(stream, script_path, modname):
    checksum_filename = get_checksum_path(script_path, modname)
    if not os.path.exists(checksum_filename):
        logger.debug("Should transpile '%s'", modname)
        return True

    with open(checksum_filename, 'r+') as checksum_file:
        existing_checksum = checksum_file.read()

    new_checksum = get_checksum(stream)
    if new_checksum != existing_checksum:
        logger.debug("Should refresh '%s' (%s)", modname, existing_checksum[:8])
        return True

    logger.debug("No need to refresh '%s' (%s)", modname, existing_checksum[:8])
    return False


@lru_cache()
def get_pycache_folder(script_path, module_name):
    """
    Gets the __pycache__ folder or PEP-3147

    Returns cache_folder path. Can be temporary.
    If so, will be cleaned automatically unless it is for __main__ module.
    """
    assert script_path.endswith('.py')

    if module_name == '__main__':
        cache_folder = tempfile.mkdtemp(suffix='__pycache__')  # Will be cleaned by grumprun
        logger.info("__main__ pycache folder: %s", cache_folder)
        return cache_folder

    ### TODO: Fix race conditions
    sys.implementation.cache_tag = GRUMPY_MAGIC_TAG
    cache_folder = os.path.abspath(os.path.normpath(
        importlib2._bootstrap.cache_from_source(script_path)
    ))
    sys.implementation.cache_tag = ORIGINAL_MAGIC_TAG
    ###

    first_existing = _get_first_existing_parent(cache_folder)

    if not os.access(first_existing, os.W_OK):
        cache_folder = SilentTemporaryDirectory(suffix='__pycache__')
        _temporary_directories.append(cache_folder)  # Hold GC until Python exits
        logger.info("Natural __pycache__ folder not available. Using %s", cache_folder.name)
        return cache_folder.name

    return cache_folder


def _get_first_existing_parent(cache_folder):
    path_parts = cache_folder.split(os.path.sep)
    if path_parts[0] == '':  # From root.
        path_parts[0] = os.path.sep

    for i, _ in enumerate(path_parts):
        subpath = os.path.join(*path_parts[:(-i or None)])
        if os.path.exists(subpath):
            return subpath


def get_gopath_folder(script_path, module_name):
    cache_folder = get_pycache_folder(script_path, module_name)
    return os.path.join(cache_folder, GOPATH_FOLDER)


def get_transpiled_base_folder(script_path, module_name):
    gopath_folder = get_gopath_folder(script_path, module_name)
    return os.path.join(gopath_folder, TRANSPILED_MODULES_FOLDER)


def get_transpiled_module_folder(script_path, module_name):
    transpiled_base_folder = get_transpiled_base_folder(script_path, module_name)
    parts = module_name.split('.')
    return os.path.join(transpiled_base_folder, *parts)


def link_parent_modules(script_path, module_name):
    package_parts = module_name.split('.')[:-1]
    if not package_parts:
        return  # No parent packages to be linked

    script_parts = script_path.split(os.sep)
    if script_parts[-1] == '__init__.py':
        script_parts = script_parts[:-1]
    if script_parts[0] == '':
        script_parts[0] = '/'
    script_parts = script_parts[:-1]

    for i, part in enumerate(reversed(package_parts)):
        parent_script = os.path.join(*script_parts[:(-i or None)])
        parent_package = '.'.join(package_parts[:(-i or None)])
        parent_package_script = imputil.find_script(parent_package, parent_script)
        if not parent_package_script:
            continue
        parent_module_folder = get_transpiled_module_folder(parent_package_script, parent_package)
        local_parent_module_folder = get_transpiled_module_folder(script_path, parent_package)

        logger.debug("Checking link of package '%s' on %s",
                     parent_package, local_parent_module_folder)
        _maybe_link_paths(os.path.join(parent_module_folder, 'module.go'),
                          os.path.join(local_parent_module_folder, 'module.go'))


def make_transpiled_module_folders(script_path, module_name):
    """
    Make the folder to store all the tree needed by the 'script_path' script

    Recursively "stomp" the files found in places that a folder is needed.
    """
    needed_folders = {
        'cache_folder': get_pycache_folder(script_path, module_name),
        'gopath_folder': get_gopath_folder(script_path, module_name),
        'transpiled_base_folder': get_transpiled_base_folder(script_path, module_name),
        'transpiled_module_folder': get_transpiled_module_folder(script_path, module_name),
    }
    for role, folder in list(needed_folders.items()):
        if os.path.isfile(folder):  # 1. Need a folder. Remove the file
            os.unlink(folder)
        if not os.path.exists(folder):  # 2. Create the needed folder
            os.makedirs(folder)

    link_parent_modules(script_path, module_name)

    result = needed_folders.copy()
    result.update({
        'checksum_file': get_checksum_path(script_path, module_name),
        'dependencies_file': get_depends_path(script_path, module_name),
    })
    return result


def _maybe_link_paths(orig, dest):
    relpath = os.path.relpath(orig, os.path.dirname(dest))
    if os.path.exists(dest) and not os.path.islink(dest):
        os.unlink(dest)

    if not os.path.exists(dest):
        try:
            os.symlink(relpath, dest)
        except OSError as err:  # Got created on an OS race condition?
            if 'exists' not in str(err):
                raise
        else:
            logger.debug('Linked %s to %s', orig, dest)
            return True
    return False
