"""`swigpy`

A supplementary tool for generating python modules with swig.
"""

#
# Copyright (c) 2014 by Pawel Tomulik <ptomulik@meil.pw.edu.pl>
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

def _prepare_kw2(env,kw):
    keys2 =  [ 'SWIG'
             , 'SWIGVERSION'
             , 'SWIGFLAGS'
             , 'SWIGDIRECTORSUFFIX'
             , 'SWIGCFILESUFFIX'
             , 'SWIGCXXFILESUFFIX'
             , 'SWIGPATH'
             , 'SWIGINCPREFIX'
             , 'SWIGINCSUFFIX'
             , 'SWIGCOM'
             , 'CPPPATH'
             , 'SHLIBPREFIX'
             , 'CFLAGS'
             , 'CXXFLAGS'
             , 'LIBS'
             , 'LIBPATH'
             , 'LDFLAGS' ]
    kw2 = { }
    for key in keys2:
        swigpy_key = "SWIGPY_%s" % key
        val = kw.get(swigpy_key, kw.get(key, env.get(swigpy_key, None)))
        if val is not None:
            kw2[key] = val
    return kw2

def _SwigPyModuleImpl(env, modname, **kw):
    from os import path
    import SCons.Util
    kw2 = _prepare_kw2(env,kw)
    shlib_prefix = kw2.get('SHLIBPREFIX', env.get('SHLIBPREFIX',''))
    parts = modname.split('.')
    m2swigfile  = kw2.get('SWIGPY_M2SWIGFILE',
                  env.get('SWIGPY_M2SWIGFILE', 
                  lambda parts: path.join(*parts) + '.i'))
    m2cfile     = kw2.get('SWIGPY_M2CFILE',
                  env.get('SWIGPY_M2CFILE', 
                  lambda parts: path.join(*parts)))
    m2shlibfile = kw2.get('SWIGPY_M2SHLIBFILE',
                  env.get('SWIGPY_M2SHLIBFILE', 
                  lambda parts: path.join(*parts)))
    swig_file  = m2swigfile(parts)
    c_file     = m2cfile(parts)
    shlib_file = m2shlibfile(parts)
    if '-c++' in kw2.get('SWIGFLAGS', env.get('SWIGFLAGS',[])):
        c_target = env.CXXFile(c_file, swig_file, **kw2)
    else:
        c_target = env.CFile(c_file, swig_file, **kw2)
    shlib_target = env.SharedLibrary(shlib_file, c_target[0], **kw2)
    return SCons.Util.flatten(c_target + [shlib_target])

def _SwigPyModule(env, modname, **kw):
    import SCons.Util
    if (not SCons.Util.is_List(modname)): modname = [modname]
    return SCons.Util.flatten([ _SwigPyModuleImpl(env, m, **kw) for m in modname ])


def generate(env):
    from distutils import sysconfig
    env.SetDefault( SWIGPY_CPPPATH      = [ sysconfig.get_python_inc() ]
                  , SWIGPY_SHLIBPREFIX  = '_'
                  , SWIGPY_SWIGFLAGS    = [ '-python', '-builtin' ])

    env.AddMethod(_SwigPyModule, 'SwigPyModule')

def exists(env):
    return 1

# Local Variables:
# # tab-width:4
# # indent-tabs-mode:nil
# # End:
# vim: set syntax=python expandtab tabstop=4 shiftwidth=4:
