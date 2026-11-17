
[app]

title = GEOSINT X
package.name = geosintx
package.domain = org.geosintx

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,db

version = 2.0.0

requirements = python3,kivy,charset-normalizer==2.1.1

orientation = portrait
fullscreen = 0

android.api = 35
android.minapi = 24
android.ndk_api = 24
android.archs = arm64-v8a
android.accept_sdk_license = True

android.allow_backup = False

[buildozer]

log_level = 2
warn_on_root = 0

[buildozer:android]

