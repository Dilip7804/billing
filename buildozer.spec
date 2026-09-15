[app]

# (str) Title of your application
title = DS World Billing

# (str) Version of your application
version = 1.0

# (str) Package name
package.name = dsworldbilling

# (str) Package domain (needed for android/ios packaging)
package.domain = org.dsworld

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let it empty to include all files)
source.exts = py,png,jpg,kv,atlas,db,csv

# (list) Application requirements
requirements = python3,kivy,kivymd,sqlite3,pillow

# (str) Supported orientations
orientation = portrait

# (list) List of services to declare
#services = 

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk_version = 25b

# (str) The Android arch to build for: arm64-v8a, armeabi-v7a, x86, x64
android.archs = armeabi-v7a

# (int) Log level (0 = error, 1 = info, 2 = debug (with command output))
log_level = 2
