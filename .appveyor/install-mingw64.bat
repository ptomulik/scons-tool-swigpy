%SHELL% "echo 'cd %APPVEYOR_BUILD_FOLDER%' | sed -e 's/^\\(\\w\\):/\\/\\l\\1/' -e 's/\\\\/\\//g' | tee -a ~/.profile"
%SHELL% "echo 'PATH=~/.local/bin:$PATH' | tee -a ~/.profile"

REM Remove all unwanted packages
%SHELL% "pacman -Qqs '(^mingw-w64-|^scons$|^python$|^python2$|^python3$)' | sort | uniq | xargs pacman -Rcs --noconfirm"

REM Upgrade remaining packages
%SHELL% "pacman -Syu --disable-download-timeout --noconfirm"
%SHELL% "pacman -Syu --disable-download-timeout --noconfirm"

REM Install what's necesary
%SHELL% "pacman -Sy --disable-download-timeout --noconfirm --needed swig mingw-w64-x86_64-toolchain mingw-w64-x86_64-%PY% mingw-w64-x86_64-%PY%-pip"
IF [%PY%]==[python2] (
  %SHELL% "test -e /mingw64/bin/python || ln -s /mingw64/bin/python2 /mingw64/bin/python"
  %SHELL% "%PY% -m pip install -r requirements2-dev.txt"
) ELSE (
  %SHELL% "%PY% -m pip install -r requirements3-dev.txt"
)
%SHELL% "%PY% -m pip install -r requirements.txt"
%SHELL% "%PY% bin/downloads.py"
