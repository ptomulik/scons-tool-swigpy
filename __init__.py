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

from .about import __version__
from .pyconf import get_py_config

import os
import sys
import SCons.Builder
import SCons.Tool
import SCons.Util
import SCons.Defaults

try:
    import site_tools.swig as swig_tool
except ImportError:
    import SCons.Tool.swig as swig_tool

try:
    from site_tools.util import ReplacingBuilder, Replacements
except ImportError:
    from sconstool.util import ReplacingBuilder, Replacements


CSuffixes = ['.c']
CXXSuffixes = ['.cc', '.cpp', '.cxx', '.c++', '.C++']
CAction = SCons.Defaults.CAction
ShCAction = SCons.Defaults.ShCAction
CXXAction = SCons.Defaults.CXXAction
ShCXXAction = SCons.Defaults.ShCXXAction
StaticObjectEmitter = SCons.Defaults.StaticObjectEmitter
SharedObjectEmitter = SCons.Defaults.SharedObjectEmitter


if SCons.Util.case_sensitive_suffixes('.c', '.C'):
    CXXSuffixes.append('.C')


swigPyVars = [
    'CCFLAGS',
    'CPPFLAGS',
    'CPPDEFINES',
    'CPPPATH',
    'SHCCFLAGS',
    'CC',
    'CFLAGS',
    'SHCC',
    'SHCFLAGS',
    'CXX',
    'CXXFLAGS',
    'SHCXX',
    'SHCXXFLAGS',
    'LINK',
    'LINKFLAGS',
    'LIBPATH',
    'LIBS',
    'SHOBJPREFIX',
    'SHOBJSUFFIX',
    'LIBPREFIX',
    'LIBSUFFIX',
    'SHLIBPREFIX',
    'SHLIBSUFFIX',
    'IMPLIBPREFIX',
    'IMPLIBSUFFIX',
    'WINDOWSEXPPREFIX',
    'WINDOWSEXPSUFFIX',
    'SWIG',
    'SWIGVERSION',
    'SWIGFLAGS',
    'SWIGDIRECTORSUFFIX',
    'SWIGCFILESUFFIX',
    'SWIGCXXFILESUFFIX',
    'SWIGPATH',
    'SWIGNCPREFIX',
    'SWIGNCSUFFIX',
    'SWIGCOM',
]


swigPyReplacements = Replacements({k: 'SWIGPY_%s' % k for k in swigPyVars})


class SwigPyShlibBuilder(ReplacingBuilder):
    def __call__(self, env, target, source, *args, **kw):
        # Preserve original $LIBPREFIXES and $LIBSUFFIXES
        ovr = {'LIBPREFIXES': [env.subst(x) for x in env['LIBPREFIXES']],
               'LIBSUFFIXES': [env.subst(x) for x in env['LIBSUFFIXES']]}
        return ReplacingBuilder.__call__(self, env, target, source, *args, **dict(ovr, **kw))


def _SwigPyModuleImpl(env, modname, **kw):
    parts = modname.split('.')
    m2swigfile  = kw.get('SWIGPY_M2SWIGFILE',
                  env.get('SWIGPY_M2SWIGFILE',
                  lambda parts: os.path.join(*parts) + '.i'))
    m2cfile     = kw.get('SWIGPY_M2CFILE',
                  env.get('SWIGPY_M2CFILE',
                  lambda parts: os.path.join(*parts)))
    m2shlibfile = kw.get('SWIGPY_M2SHLIBFILE',
                  env.get('SWIGPY_M2SHLIBFILE',
                  lambda parts: os.path.join(*parts)))
    swig_file  = m2swigfile(parts)
    c_file     = m2cfile(parts)
    shlib_file = m2shlibfile(parts)
    if '-c++' in kw.get('SWIGFLAGS', env.get('SWIGFLAGS',[])):
        c_target = env.SwigPyCXXFile(c_file, swig_file, **kw)
    else:
        c_target = env.SwigPyCFile(c_file, swig_file, **kw)
    shlib_target = env.SwigPyShlib(shlib_file, c_target[0], **kw)
    return SCons.Util.flatten(c_target + [shlib_target])


def _SwigPyModule(env, modname, **kw):
    if (not SCons.Util.is_List(modname)):
        modname = [modname]
    return SCons.Util.flatten([ _SwigPyModuleImpl(env, m, **kw) for m in modname ])


def createSwigPyCFileBuilders(env):
    (c_file, cxx_file) = SCons.Tool.createCFileBuilders(env)
    try:
        swigpy_c_file = env['BUILDERS']['SwigPyCFile']
    except KeyError:
        swigpy_c_file = ReplacingBuilder(c_file, swigPyReplacements)
        env['BUILDERS']['SwigPyCFile'] = swigpy_c_file

    try:
        swigpy_cxx_file = env['BUILDERS']['SwigPyCXXFile']
    except KeyError:
        swigpy_cxx_file = ReplacingBuilder(cxx_file, swigPyReplacements)
        env['BUILDERS']['SwigPyCXXFile'] = swigpy_cxx_file

    return (swigpy_c_file, swigpy_cxx_file)


def createSwigPyObjBuilders(env):
    try:
        swigpy_obj = env['BUILDERS']['SwigPyStaticObject']
    except KeyError:
        swigpy_obj = SCons.Builder.Builder(action={},
                                           emitter={},
                                           prefix='$SWIGPY_OBJPREFIX',
                                           suffix='$SWIGPY_OBJSUFFIX',
                                           src_builder=['SwigPyCFile', 'SwigPyCXXFile'],
                                           source_scanner=SCons.Tool.SourceFileScanner,
                                           single_source=1)
        swigpy_obj = SwigPyShlibBuilder(swigpy_obj, swigPyReplacements)
        env['BUILDERS']['SwigPyStaticObject'] = swigpy_obj
        env['BUILDERS']['SwigPyObject'] = swigpy_obj

    try:
        swigpy_shobj = env['BUILDERS']['SwigPySharedObject']
    except KeyError:
        swigpy_shobj = SCons.Builder.Builder(action={},
                                             emitter={},
                                             prefix='$SWIGPY_SHOBJPREFIX',
                                             suffix='$SWIGPY_SHOBJSUFFIX',
                                             src_builder=['SwigPyCFile', 'SwigPyCXXFile'],
                                             source_scanner=SCons.Tool.SourceFileScanner,
                                             single_source=1)
        swigpy_shobj = ReplacingBuilder(swigpy_shobj, swigPyReplacements)
        env['BUILDERS']['SwigPySharedObject'] = swigpy_shobj

    return (swigpy_obj, swigpy_shobj)


def createSwigPyShlibBuilder(env):
    try:
        swigpy_shlib = env['BUILDERS']['SwigPyShlib']
    except KeyError:
        shlib = SCons.Tool.createSharedLibBuilder(env)
        shlib = SCons.Builder.Builder(action=shlib.action,
                                      emitter='$SHLIBEMITTER',
                                      prefix='$SWIGPY_SHLIBPREFIX',
                                      suffix='$SWIGPY_SHLIBSUFFIX',
                                      target_scanner=SCons.Tool.ProgramScanner,
                                      src_suffix="$SWIGPY_SHOBJSUFFIX",
                                      src_builder=['SwigPySharedObject'])
        swigpy_shlib = SwigPyShlibBuilder(shlib, swigPyReplacements)
        env['BUILDERS']['SwigPyShlib'] = swigpy_shlib
    return swigpy_shlib


def swigPySetDefaults(env):
    # SetDefault(SWIGPY_PYTHONINCDIR=..., SWIGPY_PYTHOLIB=..., SWIGPY_PYTHOLIBDIR=...)
    env.SetDefault(**get_py_config())
    env.SetDefault(SWIGPY_SHLIBPREFIX='_')
    env.SetDefault(SWIGPY_LIBPREFIX='_')
    env.SetDefault(SWIGPY_IMPLIBPREFIX='_')
    env.SetDefault(SWIGPY_WINDOWSEXPPREFIX='_')
    if sys.platform == 'win32':
        env.SetDefault(SWIGPY_SHLIBSUFFIX='.pyd')
    #
    swigPyReplacements.inject(env, 'SetDefault')
    #
    env.AppendUnique(SWIGPY_SWIGFLAGS=[ '-python', '-builtin' ])
    env.AppendUnique(SWIGPY_CPPPATH=["$SWIGPY_PYTHONINCDIR"])
    env.AppendUnique(SWIGPY_LIBS=["$SWIGPY_PYTHONLIB"])
    env.AppendUnique(SWIGPY_LIBPATH=["$SWIGPY_PYTHONLIBDIR"])


def _setup_obj_builder(builder, c_action, cxx_action, emitter):
    for suffix in CSuffixes:
        builder.add_action(suffix, c_action)
        builder.add_emitter(suffix, emitter)
    for suffix in CXXSuffixes:
        builder.add_action(suffix, cxx_action)
        builder.add_emitter(suffix, emitter)


def generate(env):
    swig_tool.generate(env)
    (c_file, cxx_file) = createSwigPyCFileBuilders(env)
    (static_obj, shared_obj) = createSwigPyObjBuilders(env)
    _setup_obj_builder(static_obj, CAction, CXXAction, StaticObjectEmitter)
    _setup_obj_builder(shared_obj, ShCAction, ShCXXAction, SharedObjectEmitter)
    createSwigPyShlibBuilder(env)
    env.AddMethod(_SwigPyModule, 'SwigPyModule')
    swigPySetDefaults(env)

def exists(env):
    return swig_tool.exists(env)

# Local Variables:
# # tab-width:4
# # indent-tabs-mode:nil
# # End:
# vim: set syntax=python expandtab tabstop=4 shiftwidth=4:
