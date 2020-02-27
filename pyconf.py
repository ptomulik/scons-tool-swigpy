# -*- coding: utf-8 -*-
#
# Copyright (c) 2014-2018 by Pawel Tomulik <ptomulik@meil.pw.edu.pl>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE

import sysconfig
import json
import os
import sys

def python_inc_path():
    return sysconfig.get_config_var('INCLUDEPY')

def python_lib_name():
    libfile = sysconfig.get_config_var('LDLIBRARY')
    if libfile and libfile.startswith('lib') and libfile.endswith('.so'):
        return libfile[3:-3]
    return 'python' + str(sysconfig.get_config_var('VERSION'))

def python_lib_dir():
    sys.stdout.write("sysconfig.get_platform(): " + (sysconfig.get_platform() or "None") + "\n");
    if sysconfig.get_platform() in ['win32', 'win-amd64']:
        try:
            base = sys.real_prefix
        except AttributeError:
            base = sys.prefix
        sys.stdout.write("base: " + base + "\n");
        return os.path.join(base, 'libs')
    else:
        return sysconfig.get_config_var('LIBPL')

def get_py_config():
    return {'SWIGPY_PYTHONINCDIR': python_inc_path(),
            'SWIGPY_PYTHONLIBDIR': python_lib_dir(),
            'SWIGPY_PYTHONLIB': python_lib_name()}


if __name__ == '__main__':
    print(json.dumps(get_py_config()))

# Local Variables:
# # tab-width:4
# # indent-tabs-mode:nil
# # End:
# vim: set syntax=python expandtab tabstop=4 shiftwidth=4:
