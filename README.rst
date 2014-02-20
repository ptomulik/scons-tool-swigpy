scons-tool-swigpy
=================

SCons_ tool to generate Python modules using Swig_.

Usage example
-------------

Git-based projects
^^^^^^^^^^^^^^^^^^

#. Create new git repository::

      mkdir /tmp/prj && cd /tmp/prj
      touch README.rst
      git init

#. Add **scons-tool-swigpy** as submodule::

      git submodule add git://github.com/ptomulik/scons-tool-swigpy.git site_scons/site_tools/swigpy

#. Create some source files, for example ``src/hello.hpp`` and
   ``src/hello.cpp``:

   .. code-block:: cpp

      // src/hello.hpp
      #ifndef HELLO_HPP
      #define HELLO_HPP
      void hello();
      #endif

   .. code-block:: cpp

      // src/hello.cpp
      #include "hello.hpp"
      #include <iostream>
      void hello() { std::cout << "Hello" << std::endl; }

#. Create swig interface file ``src/hello.i``

    .. code-block:: swig

       // src/hello.i
       %module hello;
       %{
       #include "hello.hpp"
       %}
       %include "hello.hpp"

#. Write ``SConstruct`` file:

   .. code-block:: python


      # SConstruct
      env = Environment(tools = [ 'default', 'swigpy' ])
      SConscript('src/SConscript', exports=['env'], variant_dir='build', duplicate=0)

#. Write ``src/SConscript``:

   .. code-block:: python

      # src/SConscript
      Import(['env'])
      env.Append( SWIGPY_CPPPATH = '.' )
      env.Append( SWIGPY_LIBPATH = '.' )
      env.Append( SWIGPY_SWIGFLAGS = ['-c++'] )
      env.SharedLibrary( 'hello', ['hello.cpp'] )
      env.SwigPyModule( 'hello', SWIGPY_LIBS = 'hello' )

#. Try it out::

      scons

   This shall create a library **build/libhello.so** and all the files that
   comprise its python wrapper::

      ptomulik@tea:$ ls build/
      hello.os  hello.pyc  hello_wrap.cc  libhello.so
      hello.py  _hello.so  hello_wrap.os


#. Test the generated wrapper::

      cd build
      LD_LIBRARY_PATH='.'
      python
      >>> import hello
      >>> hello.hello()

Details
-------

Module description
^^^^^^^^^^^^^^^^^^

The module provides a ``SwigPyModule()`` builder which generates python module
based on a swig interface ``*.i`` file::

    SwigPyModule(modname, **overrides)

The **modname** is a name of the module being generated, for example ``'foo'``
or ``'foo.bar'`` (note, it's neither the source file name nor target file
name). The **overrides** are used overwrite construction variables such as
``SWIGFLAGS`` or ``CFLAGS``.

**Example 1**:

The following code expects a ``foo.i`` interface file to be present and
generates python module defined by this file.

.. code-block:: python

   SwigPyModule('foo')

**Example 2**:

The following code expects a ``foo/bar.i`` interface file to be present
and generates python module defined by this file undef ``foo`` subdirectory.

.. code-block:: python

   env.SwigPyModule('foo.bar')

Construction variables
^^^^^^^^^^^^^^^^^^^^^^

Construction variables used by ``SwigPyModule`` are summarized in the following
table. Note that there are two group of variables. The first group are the well
known construction variables. The second group are the variables prefixed with
``SWIGPY_``. The ``SWIGPY_xxx`` variables overwrite the well known variables
when generating python bindings.

========================= =============================================
Variable                   Default
========================= =============================================
SWIG
SWIGVERSION
SWIGFLAGS
SWIGDIRECTORSUFFIX
SWIGCFILESUFFIX
SWIGCXXFILESUFFIX
SWIGPATH
SWIGINCPREFIX
SWIGINCSUFFIX
SWIGCOM
CPPPATH
SHLIBPREFIX
CFLAGS
CXXFLAGS
LIBS
LIBPATH
LDFLAGS
SWIGPY_SWIG
SWIGPY_SWIGVERSION
SWIGPY_SWIGFLAGS          ``[-python', '-builtin']``
SWIGPY_SWIGDIRECTORSUFFIX
SWIGPY_SWIGCFILESUFFIX
SWIGPY_SWIGCXXFILESUFFIX
SWIGPY_SWIGPATH
SWIGPY_SWIGINCPREFIX
SWIGPY_SWIGINCSUFFIX
SWIGPY_SWIGCOM
SWIGPY_CPPPATH            ``[sysconfig.get_python_inc]``
SWIGPY_SHLIBPREFIX        ``'_'``
SWIGPY_CFLAGS
SWIGPY_CXXFLAGS
SWIGPY_LIBS
SWIGPY_LIBPATH
SWIGPY_LDFLAGS
SWIGPY_M2SWIGFILE         ``lambda parts: path.join(*parts) + '.i'``
SWIGPY_M2CFILE            ``lambda parts: path.join(*parts)``
SWIGPY_M2SHLIBFILE        ``lambda parts: path.join(*parts)``
========================= =============================================

The **SWIGPY_M2SWIGFILE** lambda determines the name of swig interface (source
file). The **SWIGPY_M2CFILE** determines the name of **C** or **C++** wrapper
file (without the suffix) being generated with **swig**. The
**SWIGPY_M2SHLIBFILE** determines the name of shared library that will contain
the wrapper binary code after compilation (without prefix and suffix). The
**parts** provided to any of these macros are the parts of **modname**, that is
they're result of ``modname.split('.')``.

.. _SCons: http://scons.org
.. _Swig: http://swig.org

LICENSE
-------

Copyright (c) 2014 by Pawel Tomulik <ptomulik@meil.pw.edu.pl>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE

.. <!--- vim: set expandtab tabstop=2 shiftwidth=2 syntax=rst: -->
