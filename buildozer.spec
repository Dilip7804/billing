[app]

# (str) Title of your application
title = DS World Billing

# (str) Package name
package.name = dsworldbilling

# (str) Package domain (needed for android packaging)
package.domain = org.dsworld

# (list) Source files to include (let it empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,pillow

# (str) Supported orientations
orientation = portrait

# (list) Permissions
android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 1
