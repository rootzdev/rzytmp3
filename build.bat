@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PY=
where py >nul 2>nul && set PY=py
if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set PY="%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if not defined PY where python >nul 2>nul && set PY=python
if not defined PY ( echo [HATA] Python bulunamadi & pause & exit /b 1 )

echo === PyInstaller + yt-dlp ===
%PY% -m pip install -U pyinstaller -r requirements.txt || ( pause & exit /b 1 )

echo.
echo === rzytmp3.exe ===
%PY% -m PyInstaller --noconfirm --clean --onefile --windowed --name rzytmp3 ^
    --icon "%~dp0icon.ico" --add-data "%~dp0icon.ico;." ^
    --workpath .build\work --specpath .build --distpath .build\dist rzytmp3.py || ( pause & exit /b 1 )

echo.
echo === ffmpeg + Deno ^(bin\^) ===
%PY% rzytmp3.py --kur
if errorlevel 1 echo [UYARI] Bazi araclar indirilemedi; zip'te eksik olacak, program acilinca "Eksikleri indir" ile tamamlanir.

for /f %%v in ('%PY% -c "import rzytmp3;print(rzytmp3.VERSION)"') do set VERSION=%%v
if exist release rmdir /s /q release
set OUT=release\RZYTMP3
mkdir "%OUT%\bin"
copy /y .build\dist\rzytmp3.exe "%OUT%\" >nul
for %%f in (ffmpeg.exe ffprobe.exe deno.exe) do if exist "bin\%%f" copy /y "bin\%%f" "%OUT%\bin\" >nul
for %%f in (README.md README.tr.md LICENSE NOTICE) do if exist "%%f" copy /y "%%f" "%OUT%\" >nul
if not exist LICENSE echo [UYARI] LICENSE yok: GPLv3 metnini klasore koy ^(GitHub'dan ya da gnu.org^).

echo.
echo === Release zip ===
powershell -NoProfile -Command "Compress-Archive -Path '%OUT%\*' -DestinationPath 'release\RZYTMP3-v%VERSION%-win64.zip' -Force"
if exist __pycache__ rmdir /s /q __pycache__
echo.
echo   GitHub Releases'a yukle: release\RZYTMP3-v%VERSION%-win64.zip
echo   ^(denemek icin: release\RZYTMP3\rzytmp3.exe^)
pause
