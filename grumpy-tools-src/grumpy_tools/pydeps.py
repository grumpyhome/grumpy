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

"""Outputs names of modules imported by a script."""


import os
import sys

from .compiler import imputil
from .compiler import util

try:
  xrange          # Python 2
except NameError:
  xrange = range  # Python 3


def main(script=None, modname=None, package_dir='', with_imports=False):
  gopath = os.environ['GOPATH']

  imports = imputil.collect_imports(modname, script, gopath, package_dir=package_dir)

  def _deps():
    names = set([modname])
    for imp in imports:
      if imp.is_native and imp.name:
        yield imp.name
      else:
        parts = imp.name.split('.')
        # Iterate over all packages and the leaf module.
        for i in range(len(parts)):
          name = '.'.join(parts[:i+1])
          if name and name not in names:
            names.add(name)
            if name.startswith('.'):
              name = name[1:]
            yield name

  if with_imports:
    return _deps(), imports
  else:
    return _deps()

