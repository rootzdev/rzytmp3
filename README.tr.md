<div align="center">

# RZYTMP3

Windows için basit bir YouTube'dan MP3 indirici.

[English](README.md) | Türkçe

[![Sürüm](https://img.shields.io/github/v/release/rootzdev/rzytmp3?color=e5383b&label=s%C3%BCr%C3%BCm)](https://github.com/rootzdev/rzytmp3/releases/latest)
[![Lisans](https://img.shields.io/badge/lisans-GPLv3-blue)](LICENSE)
[![Discord](https://img.shields.io/badge/Discord-katıl-5865f2?logo=discord&logoColor=white)](https://discord.gg/C3zPSNrTY2)

<img src="https://i.ibb.co/CSqm9H1/1.png" alt="RZYTMP3" width="760">

</div>

## Hakkında

YouTube'dan müzik indirmek için reklamsız, şüpheli sitelerle uğraşmadan kullanabileceğim küçük ve temiz bir şey istedim, ben de bunu yaptım. Linki yapıştırıyorsun (tek video ya da bütün liste), klasörü seçiyorsun, indir diyorsun. Bu kadar.

İndirme için [yt-dlp](https://github.com/yt-dlp/yt-dlp), MP3'e çevirmek için [FFmpeg](https://ffmpeg.org) kullanıyor.

## Neler yapıyor

- Tek video ya da bütün liste indiriyor, aynı anda birden fazla link yapıştırabilirsin
- Listeler kendi klasörüne iniyor, dosyalar sırayla numaralanıyor
- 128, 192, 256 ya da 320 kbps
- MP3'e kapak resmini ve şarkı adı/sanatçı bilgisini ekliyor
- Daha önce indirdiklerini hatırlıyor, aynı listeyi tekrar verince sadece yeni eklenenleri indiriyor
- Silinmiş ya da gizli videolarda durmuyor, atlayıp devam ediyor
- Türkçe ve İngilizce arayüz

## İndirme

[Releases](https://github.com/rootzdev/rzytmp3/releases/latest) sayfasından zip'i indir, bir klasöre çıkar ve `rzytmp3.exe`'yi çalıştır. Kurulum yok, ffmpeg ve Deno `bin` klasöründe hazır geliyor.

Exe imzalı olmadığı için Windows SmartScreen uyarı verebilir. "Ek bilgi" deyip "Yine de çalıştır"a bas. Kodun hepsi burada, istersen kontrol edebilir ya da kendin derleyebilirsin.

## Komut satırı

Terminalden de kullanabilirsin:

```
rzytmp3.exe "https://www.youtube.com/watch?v=..." --klasor D:\Muzik
rzytmp3.exe "https://www.youtube.com/playlist?list=..." --kalite 192
rzytmp3.exe <link> --tekli
rzytmp3.exe <link> --tekrar
```

`--tekli` link bir listeye ait olsa bile sadece o videoyu indirir, `--tekrar` "daha önce indirildi" listesini yok sayar.

## Kaynaktan çalıştırma

Python 3.10 ya da üstü lazım.

```
git clone https://github.com/rootzdev/rzytmp3.git
cd rzytmp3
install.bat
python rzytmp3.py
```

`install.bat` yt-dlp'yi kuruyor, ffmpeg ve Deno'yu `bin` klasörüne indiriyor. Exe'yi ve release zip'ini kendin yapmak istersen `build.bat`'ı çalıştır, çıktı `release` klasörüne gelir.

## Bir şey bozulursa

YouTube sık sık bir şeyleri değiştiriyor ve bazen indirme çalışmayı bırakıyor. Genelde yt-dlp'yi güncellemek düzeltiyor: en yeni release'i indir, kaynaktan çalıştırıyorsan `install.bat`'ı tekrar çalıştır. Yine olmazsa issue aç ya da Discord'dan yaz.

## Lisans

GPLv3, birkaç ek şart da [NOTICE](NOTICE) dosyasında. Ücretsiz kullanabilir, değiştirebilir ve paylaşabilirsin. Değiştirilmiş bir sürümünü yayınlarsan GPLv3 ile açık kaynak kalmalı, telif satırım ve uygulamadaki "Developed by rootzdev" yazısı korunmalı.

Uygulama hiçbir garanti olmadan sunuluyor, nasıl kullanıldığından ben sorumlu değilim. Kişisel kullanım için yapıldı, telif haklarına ve YouTube kurallarına uymak sana kalmış.

---

<div align="center">

rootzdev tarafından yapıldı · [Discord](https://discord.gg/C3zPSNrTY2)

</div>
