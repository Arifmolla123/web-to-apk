[app]
title = SpyAgent
package.name = spyagent
package.domain = org.survivors
source.dir = .
source.include_exts = py,png
version = 1.0
requirements = python3,requests,plyer
permissions = INTERNET,READ_SMS,ACCESS_FINE_LOCATION,READ_CONTACTS,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.permissions = INTERNET,READ_SMS,ACCESS_FINE_LOCATION,READ_CONTACTS,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.accept_sdk_license = True
android.skip_update = False
fullscreen = 0
orientation = portrait

[buildozer]
log_level = 2
warn_on_root = 1
