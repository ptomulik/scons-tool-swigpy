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

__docformat__ = "restructuredText"

"""
Test example from README.rst
"""

import sys
import os
import TestSCons

_dll = TestSCons._dll
dll_ = TestSCons.dll_
_python_ = TestSCons._python_

if sys.platform == 'win32':
    test = TestSCons.TestSCons(program='scons.bat', interpreter=None)
    _ext = '.pyd'
else:
    test = TestSCons.TestSCons()
    _ext = _dll

if sys.platform == 'win32':
    appveyor_image = os.environ.get('APPVEYOR_BUILD_WORKER_IMAGE', '')
    if appveyor_image.lower() == 'mingw':
        _tools_ = r"['mingw', 'swigpy']"
    else:
        _tools_ = r"['default', 'swigpy']"
    _env_args_ = "tools=%s, ENV={'TEMP':'.', 'PATH': %r}" % (_tools_, os.environ['PATH'])
    _include_windows_i_ = '%include <windows.i>'
    _helloapi_ = '__declspec(dllexport) void'
else:
    _env_args_ = "tools=['default', 'swigpy']"
    _include_windows_i_ = ''
    _helloapi_ = 'void'


test.subdir(['site_scons'])
test.subdir(['site_scons', 'site_tools'])
test.subdir(['site_scons', 'site_tools', 'swigpy'])
test.file_fixture('../../../../__init__.py','site_scons/site_tools/swigpy/__init__.py')
test.file_fixture('../../../../about.py','site_scons/site_tools/swigpy/about.py')
test.file_fixture('../../../../pyconf.py','site_scons/site_tools/swigpy/pyconf.py')

test.subdir(['src'])

test.write('SConstruct', """\
# SConstruct
import os
env = Environment( %(_env_args_)s )
SConscript('src/SConscript', exports=['env'], variant_dir='build', duplicate=0)
""" % locals())

test.write('src/SConscript', """\
# src/SConscript
Import(['env'])
env.Append( SWIGPY_CPPPATH = ['.'] )
env.Append( SWIGPY_LIBPATH = ['.'] )
env.Append( SWIGPY_SWIGFLAGS = ['-c++'] )
env.SharedLibrary( 'hello', ['hello.cpp'] )
env.SwigPyModule( 'hello', SWIGPY_LIBS = ['$SWIGPY_PYTHONLIB', 'hello'] )
""")

test.write('src/hello.hpp', """\
// src/hello.hpp
#ifndef HELLO_HPP
#define HELLO_HPP
%(_helloapi_)s hello();
#endif
""" % locals())

test.write('src/hello.cpp', """\
// src/hello.cpp
#include "hello.hpp"
#include <iostream>
void hello() { std::cout << "Hello" << std::endl; }
""")

test.write('src/hello.i', """\
// src/hello.i
%%module hello;
%%{
#include "hello.hpp"
%%}
%(_include_windows_i_)s
%%include "hello.hpp"
""" % locals())

test.run()

test.must_exist('build/hello_wrap.cc')
test.must_exist('build/%(dll_)shello%(_dll)s' % locals())
test.must_exist('build/_hello%(_ext)s' % locals())
test.must_exist('build/hello.py')

test.write('build/test.py', """\
#!%(_python_)s
import hello
hello.hello()
""" % locals())

if sys.platform == 'win32':
    os.environ['PATH'] = os.path.pathsep.join([test.workpath('build'), os.environ['PATH']])
    os.environ['PYTHONPATH'] = test.workpath('build')
else:
    os.environ['LD_LIBRARY_PATH'] = test.workpath('build')
test.run(chdir='build', program='test.py', interpreter=_python_, stdout='Hello\n', stderr=None)


test.pass_test()

# Local Variables:
# # tab-width:4
# # indent-tabs-mode:nil
# # End:
# vim: set syntax=python expandtab tabstop=4 shiftwidth=4:
