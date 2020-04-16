# -*- coding: utf-8 -*-
#
# Copyright (c) 2014-2020 by Paweł Tomulik <ptomulik@meil.pw.edu.pl>
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
import sysconfig
import subprocess
import TestSCons
import TestCmd

_dll = TestSCons._dll
dll_ = TestSCons.dll_
_python_ = TestSCons._python_


if sys.platform == 'win32':
    _ext = '.pyd'
else:
    _ext = _dll


_scons_ = TestCmd.where_is('scons')
if _scons_ is not None:
    # Find the actual scons Python script. We believe that the scons found
    # withing PATH is the one installed for our _python_.
    if _scons_[-4:].upper() in ['.BAT']:
        # On win32 the python script is found alongside with the .BAT script.
        # where_is() returns 'scons.BAT', so we need to strip out the extension.
        _scons_ = _scons_[:-4]
    test = TestSCons.TestSCons(program=_scons_, interpreter=_python_)
else:
    test = TestSCons.TestSCons(interpreter=_python_)


test.subdir(['site_scons'])
test.subdir(['site_scons', 'site_tools'])
test.subdir(['site_scons', 'site_tools', 'swigpy'])
test.file_fixture('../../../../__init__.py','site_scons/site_tools/swigpy/__init__.py')
test.file_fixture('../../../../about.py','site_scons/site_tools/swigpy/about.py')
test.file_fixture('../../../../pyconf.py','site_scons/site_tools/swigpy/pyconf.py')


if sysconfig.get_platform().startswith('mingw'):
    # Set 'mingw' tool, because 'default' prefers MS Visual C Compiler
    _tools_ = r"['mingw', 'swigpy']"
else:
    _tools_ = r"['default', 'swigpy']"

_path_ = os.environ['PATH']
if sys.platform == 'win32':
    _env_args_ = "tools=%(_tools_)s, ENV={'TEMP':'.', 'PATH': r%(_path_)r}" % locals()
else:
    _env_args_ = "tools=%(_tools_)s" % locals()

# support compiling and testing against custom python interpreter (other than the one running this script).

_swigpy_python_ = os.environ.get('SWIGPY_PYTHON', _python_)

try:
    _swigpy_pyconf_ = os.environ['SWIGPY_PYCONF']
except KeyError:
    if _swigpy_python_ != _python_:
        _swigpy_pyconf_ = subprocess.check_output([_swigpy_python_, 'site_scons/site_tools/swigpy/pyconf.py'], universal_newlines=True)
    else:
        _swigpy_pyconf_ = None

if _swigpy_pyconf_ is not None:
    _env_args_ = _env_args_ + ', **%(_swigpy_pyconf_)s' % locals()

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
env.SharedLibrary('hello', ['hello.cpp'], CPPDEFINES={'BUILDING_HELLO': '1'})
env.SwigPyModule('hello', SWIGPY_LIBS = ['$SWIGPY_PYTHONLIB', 'hello'])
""")

test.write('src/hello.hpp', """\
// src/hello.hpp
#ifndef HELLO_HPP
#define HELLO_HPP
#ifdef _WIN32
# ifdef BUILDING_HELLO
#  define HELLO_API __declspec(dllexport)
# else
#  define HELLO_API __declspec(dllimport)
# endif
#else
# define HELLO_API
#endif
extern void HELLO_API hello();
#endif
""" % locals())

test.write('src/hello.cpp', """\
// src/hello.cpp
#include "hello.hpp"
#include <iostream>
void HELLO_API hello() { std::cout << "Hello" << std::endl; }
""")

test.write('src/hello.i', """\
// src/hello.i
%%module hello;
%%{
#include "hello.hpp"
%%}
#define HELLO_API
%%include "hello.hpp"
""" % locals())

test.run()

test.must_exist('build/hello_wrap.cc')
test.must_exist('build/%(dll_)shello%(_dll)s' % locals())
test.must_exist('build/_hello%(_ext)s' % locals())
test.must_exist('build/hello.py')

test.write('build/test.py', """\
#!%(_swigpy_python_)s
import hello
hello.hello()
""" % locals())

if sys.platform == 'win32':
    os.environ['PATH'] = os.path.pathsep.join([test.workpath('build'), os.environ['PATH']])
    os.environ['PYTHONPATH'] = test.workpath('build')
else:
    os.environ['LD_LIBRARY_PATH'] = test.workpath('build')
test.run(chdir='build', program='test.py', interpreter=_swigpy_python_, stdout='Hello\n', stderr=None)


test.pass_test()

# Local Variables:
# # tab-width:4
# # indent-tabs-mode:nil
# # End:
# vim: set syntax=python expandtab tabstop=4 shiftwidth=4:
