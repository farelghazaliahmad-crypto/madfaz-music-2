[app]
title = MADFAZ Music
package.name = madfazmusic
package.domain = org.madfaz
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.2
requirements = python3, kivy==2.3.0, kivymd==1.2.0, ytmusicapi, yt-dlp, requests, urllib3, certifi, charset-normalizer, idna
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
log_level = 2
android.copy_libs = 1

[buildozer]
log_level = 2
warn_on_root = 1
