#!/usr/bin/env python
# coding=utf-8

# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A Python -> Go transcompiler."""

from __future__ import unicode_literals

import argparse
import os
import sys
from StringIO import StringIO
import textwrap
import pickle
import logging

import dill

from .compiler import block
from .compiler import imputil
from .compiler import stmt
from .compiler import util
from .compiler.parser import patch_pythonparser
import pythonparser
from .pep_support.pep3147pycache import make_transpiled_module_folders, should_refresh, set_checksum, fixed_keyword
from . import pydeps

logger = logging.getLogger(__name__)


def _parse_and_visit(stream, script, modname):
  patch_pythonparser()
  gopath = os.environ['GOPATH']

  stream.seek(0)
  py_contents = stream.read()
  mod = pythonparser.parse(py_contents)

  # Do a pass for compiler directives from `from __future__ import *` statements
  future_node, future_features = imputil.parse_future_features(mod)

  importer = imputil.Importer(gopath, modname, script,
                              future_features.absolute_import)
  full_package_name = modname.replace('.', '/')
  mod_block = block.ModuleBlock(importer, full_package_name, script,
                                py_contents, future_features)

  visitor = stmt.StatementVisitor(mod_block, future_node)
  # Indent so that the module body is aligned with the goto labels.
  with visitor.writer.indent_block():
    visitor.visit(mod)
  return visitor, mod_block


def _collect_deps(script, modname, pep3147_folders, from_cache=False, update_cache=True):
  if from_cache:
    try:
      with open(pep3147_folders['dependencies_file']) as deps_dumpfile:
        deps, import_objects = pickle.load(deps_dumpfile)
      return deps, import_objects
    except Exception as err:
      # Race conditions with other scripts running or stale/broken dump
      logger.info("Could not load dependencies of '%s' from cache.", modname)

  if os.path.exists(script):
    deps, import_objects = pydeps.main(script, modname, with_imports=True) #, script, gopath)
  elif os.path.exists(os.path.join(pep3147_folders['cache_folder'], os.path.basename(script))):
    deps, import_objects = pydeps.main(
      os.path.join(pep3147_folders['cache_folder'], os.path.basename(script)),
      modname,
      package_dir=os.path.dirname(script),
      with_imports=True,
    )
  else:
    raise NotImplementedError()

  deps = set(deps).difference(_get_parent_packages(modname))

  if update_cache:
    try:
      with open(pep3147_folders['dependencies_file'], 'wb') as deps_dumpfile:
        pickle.dump((deps, import_objects), deps_dumpfile)
    except Exception as err:
      logger.warning("Could not store dependencies of '%s' on cache: %s", modname, err)
    else:
      logger.debug("Dependencies file regenerated")
  return deps, import_objects


def _recursively_transpile(import_objects, ignore=None):
  ignore = ignore or set()
  for imp_obj in import_objects:
    if not imp_obj.is_native:
      name = imp_obj.name[1:] if imp_obj.name.startswith('.') else imp_obj.name

      if imp_obj.name in ignore:
        # logger.debug("Already collected '%s'. Ignoring", imp_obj.name)
        continue  # Do not do cyclic imports

      if not imp_obj.script:
        logger.debug("Importing '%s' will raise ImportError", imp_obj.name)
        ignore.add(imp_obj.name)
        continue  # Let the ImportError raise on run time

      # Recursively compile the discovered imports
      result = main(stream=open(imp_obj.script), modname=name, pep3147=True,
                    recursive=True, return_gocode=False, return_deps=True,
                    ignore=ignore)
      if name.endswith('.__init__'):
        name = name.rpartition('.__init__')[0]
        result = main(stream=open(imp_obj.script), modname=name, pep3147=True,
                      recursive=True, return_gocode=False, return_deps=True,
                      ignore=ignore)
      yield result['deps']


def _transpile(script, modname, imports, visitor, mod_block):
  file_buffer = StringIO()
  writer = util.Writer(file_buffer)
  tmpl = textwrap.dedent("""\
      package $package
      import (
      \tπg "grumpy"
      $imports
      )
      var Code *πg.Code
      func init() {
      \tCode = πg.NewCode("<module>", $script, nil, 0, func(πF *πg.Frame, _ []*πg.Object) (*πg.Object, *πg.BaseException) {
      \t\tvar πR *πg.Object; _ = πR
      \t\tvar πE *πg.BaseException; _ = πE""")
  writer.write_tmpl(tmpl, package=fixed_keyword(modname.split('.')[-1]),
                    script=util.go_str(script), imports=imports)
  with writer.indent_block(2):
    for s in sorted(mod_block.strings):
      writer.write('ß{} := πg.InternStr({})'.format(s, util.go_str(s)))
    writer.write_temp_decls(mod_block)
    writer.write_block(mod_block, visitor.writer.getvalue())
  writer.write_tmpl(textwrap.dedent("""\
    \t\treturn nil, πE
    \t})
    \tπg.RegisterModule($modname, Code)
    }"""), modname=util.go_str(modname))
  return file_buffer


def main(stream=None, modname=None, pep3147=False, recursive=False, return_gocode=True, ignore=None, return_deps=False):
  ignore = ignore or set()
  ignore.add(modname)
  script = os.path.abspath(stream.name)
  assert script and modname, 'Script "%s" or Modname "%s" is empty' % (script, modname)

  gopath = os.getenv('GOPATH', None)
  if not gopath:
    raise RuntimeError('GOPATH not set')

  pep3147_folders = make_transpiled_module_folders(script, modname)
  will_refresh = should_refresh(stream, script, modname)

  deps, import_objects = _collect_deps(script, modname, pep3147_folders, from_cache=(not will_refresh))
  deps = set(deps)
  imports = ''.join('\t// _ "' + _package_name(name) + '"\n' for name in deps)

  if will_refresh or return_gocode:
    visitor, mod_block = _parse_and_visit(stream, script, modname)
    file_buffer = _transpile(script, modname, imports, visitor, mod_block)
  else:
    file_buffer = None

  if recursive:
    transitive_deps = _recursively_transpile(import_objects, ignore=ignore)

  if pep3147:
    new_gopath = pep3147_folders['gopath_folder']
    if new_gopath not in os.environ['GOPATH'].split(os.pathsep):
      os.environ['GOPATH'] += os.pathsep + new_gopath

    if file_buffer:
      file_buffer.seek(0)
      mod_dir = pep3147_folders['transpiled_module_folder']
      with open(os.path.join(mod_dir, 'module.go'), 'w+') as transpiled_file:
        transpiled_file.write(file_buffer.read())
      set_checksum(stream, script, modname)

  result = {}
  if return_gocode:
    assert file_buffer, "Wrong logic paths. 'file_buffer' should be available here!"
    file_buffer.seek(0)
    result['gocode'] = file_buffer.read()
  if return_deps:
    result['deps'] = frozenset(deps.union(*transitive_deps))
  return result


def _package_name(modname):
  if modname.startswith('__go__/'):
    return '__python__/' + modname
  return '__python__/' + fixed_keyword(modname).replace('.', '/')


def _get_parent_packages(modname):
  package_parts = modname.split('.')
  parent_parts = package_parts[:-1]
  for i, _ in enumerate(parent_parts):
    yield '.'.join(parent_parts[:(-i or None)])
