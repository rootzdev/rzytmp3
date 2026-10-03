@echo off
chcp 65001 >nul
cd /d "%~dp0"
call :find_python || exit /b 1

echo === yt-dlp ===
%PY% -m pip install -U -r requirements.txt
if errorlevel 1 ( echo [HATA] pip basarisiz & pause & exit /b 1 )

echo.
echo === ffmpeg + Deno ^(bin\^) ===
%PY% rzytmp3.py --kur
echo.
echo === Bitti. Calistirmak icin: %PY% rzytmp3.py  ^(ya da build.bat ile exe yap^) ===
pause
exit /b 0

:find_python
set PY=
where py >nul 2>nul && set PY=py
if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set PY="%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if not defined PY where python >nul 2>nul && set PY=python
if not defined PY ( echo [HATA] Python bulunamadi. https://www.python.org/downloads/ & pause & exit /b 1 )
exit /b 0
