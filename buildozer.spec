[app]
title = 职业测评
package.name = careertest
package.domain = org.example

source.dir = .
source.include_exts = py,json,otf,png,jpg
source.exclude_dirs = preview,dist,build,bin,.git,.github,__pycache__,shots,sbti_shots,v3,v4,new_apk,apk_out,logs_extract
source.exclude_patterns = test_drive.py, drive_slow.py, mini_result.py, mini_screens.py, console_version.py, dev_show.py, dev_flow.py, dev_tall.py

version = 1.1

# KivyMD 2.0 在安卓上不需要 materialshapes（那是 LoadingIndicator 用的），
# 所以这里不列 pycairo，避免触发它的本地编译。
requirements = python3,kivy==2.3.1,kivymd==2.0.0,materialyoucolor==3.0.4,asynckivy==0.6.4,asyncgui==0.6.3,pillow

orientation = portrait
fullscreen = 0

android.api = 34
android.minapi = 24
android.archs = arm64-v8a
android.accept_sdk_license = True
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
