#! /usr/bin/env python

import subprocess
import argparse
import tempfile
import shutil
import tarfile
import zipfile
import string
import glob
import os
import sys
import platform
import io

try:
    # Python 3
    from urllib.request import urlopen, urlretrieve
except ImportError:
    # Python 2
    from urllib2 import urlopen
    from urllib import urlretrieve

def untar(tar, **kw):
    # Options
    strip_components = kw.get('strip_components', 0)
    member_name_filter = kw.get('member_name_filter', lambda x : True)
    path = kw.get('path', '.')
    # Untar
    members = [m for m in tar.getmembers() if len(m.name.split('/')) > strip_components]
    if strip_components > 0:
        for m in members:
            m.name = '/'.join(m.name.split('/')[strip_components:])

    members = [m for m in members if member_name_filter(m.name) ]
    tar.extractall(path = path, members = members)

def urluntar(url, **kw):
    # Download the tar file
    tar = tarfile.open(fileobj = io.BytesIO(urlopen(url).read()))
    untar(tar, **kw)
    tar.close()

def unzip(zf, **kw):
    # Options
    strip_components = kw.get('strip_components', 0)
    member_name_filter = kw.get('member_name_filter', lambda x : True)
    path = kw.get('path', '.')
    # Untar
    members = [ m for m in zf.namelist() if member_name_filter(m) ]
    zf.extractall(path = path, members = members)

def urlunzip(url, **kw):
    # Download the zip file
    zf = zipfile.ZipFile(file = io.BytesIO(urlopen(url).read()))
    unzip(zf, **kw)
    zf.close()

def info(msg, **kw):
    try: quiet = kw['quiet']
    except KeyError: quiet = False
    if not quiet:
        sys.stdout.write("%s: info: %s\n" % (_script, msg))

def warn(msg, **kw):
    try: quiet = kw['quiet']
    except KeyError: quiet = False
    if not quiet:
        sys.stderr.write("%s: warning: %s\n" % (_script, msg))
    untar(tar, **kw)
    tar.close()

def download_texlive_installer(**kw):
    url = kw.get('installer_url')
    fnames = {
        'Windows' : 'install-tl.zip',
        'Linux'   : 'install-tl-unx.tar.gz'
    }
    if not url:
        url_base = kw.get('installer_url_base')
        if not url_base:
            url_base ="http://sunsite.icm.edu.pl/pub/tex/systems/texlive"
        try:
            fname = fnames[platform.system()]
        except KeyError:
            raise RuntimeError("unsupported OS %s" % platform.system())
        url="%s/tlnet/%s" % (url_base, fname)

    tempdir = kw['tempdir']
    instfile = os.path.join(tempdir, fname)
    info("downloading '%s' -> '%s'" % (url,instfile))
    if platform.system() == 'Windows':
        urlunzip(url,path = tempdir)
    elif platform.system() == 'Linux':
        urluntar(url,path = tempdir, strip_components = 1)
    else:
        raise RuntimeError("unsuported OS %s" % platform.system())
    return 0

def prepare_texlive_profile(**kw):
    profile_in = kw.get('profile')
    profile_out = os.path.join(kw['tempdir'], "texlive.profile")
    if not profile_in:
        profile_map = {
            'Windows' : 'texlive-default-win32.profile',
            'Linux'   : 'texlive-default-linux.profile'
        }
        try:
            profile_in = profile_map[platform.system()]
        except KeyError:
            raise RuntimeError("unsuported OS %s" % platform.system())
        profile_in = os.path.join(_scriptdir, profile_in)
    with open(profile_in) as fin:
        tpl = string.Template(fin.read())
        content = tpl.safe_substitute(os.environ.copy())
        with open(profile_out, 'w') as fout:
            fout.write(content)

def install_texlive(**kw):
    tempdir = kw['tempdir']
    if platform.system() == 'Windows':
        ptr = os.path.join(tempdir,'install-tl-*','install-tl-windows.bat')
        lst = glob.glob(ptr)
        if not lst:
            warn("coult not find install-tl-windows.bat", **kw)
            return 2
        cmd = lst[0]
    elif platform.system() == 'Linux':
        cmd = os.path.join(tempdir,'install-tl')
    else:
        raise RuntimeError("unsuported OS %s" % platform.system())

    repository = kw.get('repository')

    profile = os.path.join(tempdir, 'texlive.profile')

    args = [cmd, '-profile', profile]
    if repository:
        args += ['-repository', repository]

    info("starting TeX instaler", **kw)
    info("%s" % map(lambda x : str(x), args), **kw)
    spkw = {'env': os.environ.copy(), 'stdin': subprocess.PIPE}
    if sys.version_info < (3,7):
        spkw['universal_newlines'] = True
    else:
        spkw['text'] = True
    sp = subprocess.Popen(args, **spkw)
    if platform.system() == 'Windows':
        # Answer to "Press any key to continue..."
        sp.stdin.write("\n")
    sp.stdin.close()
    sp.wait()


def download_and_install_texlive(**kw):
    download_texlive_installer(**kw)
    prepare_texlive_profile(**kw)
    install_texlive(**kw)


def main(**kw):
    info("creating temporary directory", **kw)
    tempdir = tempfile.mkdtemp(prefix = 'install-tex-')
    info("created temporary directory '%s'" % tempdir, **kw)

    kw['tempdir'] = tempdir

    if(_args.distro.lower() == 'texlive'):
        download_and_install_texlive(**kw)
    else:
        warn("unsupported distro: %r")

    info("deleting temporary directory '%s'" % tempdir, **kw)
    shutil.rmtree(tempdir, ignore_errors=True)
    info("deleted temporary directory '%s'" % tempdir, **kw)

_script = os.path.basename(sys.argv[0])
_scriptabs = os.path.realpath(sys.argv[0])
_scriptdir = os.path.dirname(_scriptabs)
_topsrcdir = os.path.realpath(os.path.join(_scriptdir, '..'))
_parser = argparse.ArgumentParser(
    prog=_script,
    description="""\
    Downloads and installs TeX distribution. Used mainly on Continuous
    Integration systems.
    """
)

_parser.add_argument('--quiet',
                      action='store_true',
                      help='do not print messages')
_parser.add_argument('--distro',
                      choices=['texlive'],
                      default='texlive',
                      help='selects a distribution to be installed')
_parser.add_argument('--installer-url',
                      help='url used to retrieve TeX installer from')
_parser.add_argument('--profile',
                      help='path to texlive profile for unattended installation')
_parser.add_argument('--repository', help='path/url to package repository')

_args = _parser.parse_args()
main(**vars(_args))

# Local Variables:
# # tab-width:4
# # indent-tabs-mode:nil
# # End:
# vim: set syntax=python expandtab tabstop=4 shiftwidth=4:
