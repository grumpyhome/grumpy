#!/usr/bin/env python

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

"""grumprun compiles and runs a snippet of Python using Grumpy.

Usage: $ grumprun -m <module>             # Run the named module.
       $ echo 'print "hola!"' | grumprun  # Execute Python code from stdin.
"""

from future import standard_library
standard_library.install_aliases()
from builtins import open
import argparse
import os
import random
import shutil
import string
import subprocess
import sys
import tempfile
import logging
from io import StringIO

from .compiler import imputil
from .pep_support.pep3147pycache import make_transpiled_module_folders
from . import grumpc

logger = logging.getLogger(__name__)

TRACEBACK_DEPENDENCIES = [
  '__go__/grumpy',
  '__go__/io/ioutil',
  '__go__/os',
  '__go__/path/filepath',
  '__go__/reflect',
  '__go__/runtime',
  '__go__/sync',
  '__go__/syscall',
  '__go__/time',
  '__go__/unicode',
  '_syscall',
  'linecache',
  'os',
  'os/path',
  'stat',
  'sys',
  'traceback',
  'types',
]

module_tmpl = string.Template("""\
package main
import (
\t"os"
\t"grumpy"
\tmod "$package"
$imports
)
func main() {
\tgrumpy.ImportModule(grumpy.NewRootFrame(), "traceback")
\tos.Exit(grumpy.RunMain(mod.Code))
}
""")


def main(stream=None, modname=None, pep3147=False, clean_tempfolder=True, go_action='run'):
  assert pep3147, 'It is no longer optional'
  assert (stream is None and modname) or (stream.name and not modname)

  gopath = os.environ['GOPATH']

  # CPython does not cache the __main__. Should I?
  try:
    script = None
    if modname and not stream:  # TODO: move all this `if modname` to the CLI handling?
      # Find the script associated with the given module.
      for d in gopath.split(os.pathsep):
        script = imputil.find_script(
          os.path.join(d, 'src', '__python__'), modname)
        if script:
          break
      if not script:
        for d in sys.path:
          script = imputil.find_script(d, modname, main=True)
          if script:
            break
      if not script:
        script = imputil.find_script(os.getcwd(), modname, main=True)
      if not script:
        raise RuntimeError("can't find module '%s'", modname)

      stream = StringIO(open(script).read())
      if script.endswith('__main__.py'):
        stream.name = script
      else:
        stream.name = '__main__.py'

    script = os.path.abspath(stream.name)
    modname = '__main__'

    pep3147_folders = make_transpiled_module_folders(script, modname)
    workdir = pep3147_folders['transpiled_base_folder']

    # Generate a dummy python script on the 'cache_folder'
    script_name = os.path.join(pep3147_folders['cache_folder'], os.path.basename(script))
    with open(script_name, 'wb') as script_file:
      stream.seek(0)
      script_file.write(stream.read())

    py_dir = os.path.join(workdir, 'src', '__python__')

    mod_dir = pep3147_folders['transpiled_module_folder']

    ## TODO: Manage the STDIN and `-c` scripts situation
    # script = os.path.join(py_dir, 'module.py')
    # with open(script, 'w') as f:
    #   f.write(stream.read())
    ##

    gopath_folder = pep3147_folders['gopath_folder']
    os.environ['GOPATH'] = os.pathsep.join([gopath_folder, gopath]) #, workdir])

    # Compile the dummy script to Go using grumpc.
    with open(os.path.join(mod_dir, 'module.go'), 'w+', encoding='utf-8') as dummy_file:
      result = grumpc.main(stream, modname=modname, pep3147=True, recursive=True, return_deps=True)
      transpiled, deps = result['gocode'], result['deps']
      dummy_file.write(transpiled)

    # Make sure traceback is available in all Python binaries.
    names = sorted(set(['traceback'] + TRACEBACK_DEPENDENCIES).union(deps))

    go_main = os.path.join(workdir, 'main.go')
    package = grumpc._package_name(modname)
    imports = ''.join('\t_ "' + grumpc._package_name(name) + '"\n' for name in names)
    with open(go_main, 'w') as f:
      f.write(module_tmpl.substitute(package=package, imports=imports))
    logger.info('`go run` GOPATH=%s', os.environ['GOPATH'])
    if go_action == 'run':
      subprocess_cmd = 'go run ' + go_main
    elif go_action == 'build':
      subprocess_cmd = 'go build ' + go_main
    elif go_action == 'debug':
      subprocess_cmd = 'dlv debug --listen=:2345 --log ' + go_main
    else:
      raise NotImplementedError('Go action "%s" not implemented' % go_action)
    logger.debug('Starting subprocess: `%s`', subprocess_cmd)
    return subprocess.Popen(subprocess_cmd, shell=True).wait()
  finally:
    if 'pep3147_folders' in locals():
      if clean_tempfolder:
        shutil.rmtree(pep3147_folders['cache_folder'], ignore_errors=True)
      else:
        logger.warning('not cleaning the temporary pycache folder: %s', pep3147_folders['cache_folder'])
