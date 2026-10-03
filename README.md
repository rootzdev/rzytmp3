<div align="center">

# RZYTMP3

Simple YouTube to MP3 downloader for Windows.

English | [Türkçe](README.tr.md)

[![Release](https://img.shields.io/github/v/release/rootzdev/rzytmp3?color=e5383b)](https://github.com/rootzdev/rzytmp3/releases/latest)
[![License](https://img.shields.io/badge/license-GPLv3-blue)](LICENSE)
[![Discord](https://img.shields.io/badge/Discord-join-5865f2?logo=discord&logoColor=white)](https://discord.gg/C3zPSNrTY2)

<img src="https://i.ibb.co/CSqm9H1/1.png" alt="RZYTMP3" width="760">

</div>

## About

I wanted something small and clean to grab music from YouTube without ads or shady websites, so I made this. Paste a link (a single video or a whole playlist), pick a folder, hit download. That's it.

It uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) for downloading and [FFmpeg](https://ffmpeg.org) for converting to MP3.

## What it does

- Downloads single videos or full playlists, you can paste several links at once
- Playlists get their own folder and the files are numbered in order
- 128, 192, 256 or 320 kbps
- Adds the cover art and title/artist tags to the MP3
- Remembers what you already downloaded, so running the same playlist again only grabs the new songs
- Skips deleted or private videos instead of stopping
- Turkish and English interface

## Download

Get the zip from the [Releases](https://github.com/rootzdev/rzytmp3/releases/latest) page, extract it and run `rzytmp3.exe`. Nothing to install, ffmpeg and Deno are already in the `bin` folder.

Windows SmartScreen might complain because the exe isn't signed. Click "More info" and then "Run anyway". The source is all here if you want to check it or build it yourself.

## Command line

You can also use it from a terminal:

```
rzytmp3.exe "https://www.youtube.com/watch?v=..." --folder D:\Music
rzytmp3.exe "https://www.youtube.com/playlist?list=..." --quality 192
rzytmp3.exe <link> --single
rzytmp3.exe <link> --redownload
```

`--single` downloads only the video even if the link is part of a playlist, `--redownload` ignores the "already downloaded" list.

## Running from source

You need Python 3.10 or newer.

```
git clone https://github.com/rootzdev/rzytmp3.git
cd rzytmp3
install.bat
python rzytmp3.py
```

`install.bat` installs yt-dlp and puts ffmpeg and Deno into `bin`. To make the exe and the release zip yourself, run `build.bat`. The output goes to the `release` folder.

## If something breaks

YouTube changes things pretty often and sometimes downloads stop working. Usually updating yt-dlp fixes it: grab the newest release, or run `install.bat` again if you're running from source. If that doesn't help, open an issue or ask on Discord.

## License

GPLv3, with a couple of extra terms in [NOTICE](NOTICE). You can use it, change it and share it for free. If you publish a modified version, keep it open source under GPLv3, keep my copyright notice and keep the "Developed by rootzdev" credit in the app.

The app comes with no warranty and I'm not responsible for how it's used. It's meant for personal use. Make sure you respect copyright and YouTube's terms.

---

<div align="center">

Made by rootzdev · [Discord](https://discord.gg/C3zPSNrTY2)

</div>
