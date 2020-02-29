%SHELL% "echo 'cd %APPVEYOR_BUILD_FOLDER%' | sed -e 's/^\\(\\w\\):/\\/\\l\\1/' -e 's/\\\\/\\//g' | tee -a ~/.profile"
%SHELL% "echo 'PATH=~/.local/bin:$PATH' | tee -a ~/.profile"

%SHELL% "pacman -Sy --disable-download-timeout --noconfirm --needed swig mingw-w64-x86_64-toolchain mingw-w64-x86_64-%PY% mingw-w64-x86_64-%PY%-pip"
%SHELL% "%PY% -m pip install -r requirements.txt"
IF [%PY%]==[python2] (
  %SHELL% "pacman -Rcs --noconfirm mingw-w64-x86_64-python3"
  %SHELL% "test -e /mingw64/bin/python || ln -s /mingw64/bin/python2 /mingw64/bin/python"
  %SHELL% "%PY% -m pip install -r requirements2-dev.txt"
) ELSE (
  %SHELL% "pacman -Rcs --noconfirm mingw-w64-x86_64-python2"
  %SHELL% "test -e /mingw64/bin/python || ln -s /mingw64/bin/python3 /mingw64/bin/python"
  %SHELL% "%PY% -m pip install -r requirements3-dev.txt"
)
%SHELL% "%PY% bin/downloads.py"
