from madman.models import *
from django.contrib import admin 
from mptt.admin import MPTTModelAdmin

admin.site.register(UserProfile) 
admin.site.register(MediaTree)
admin.site.register(MediaType)
admin.site.register(MediaLink)
admin.site.register(MediaLocation)
admin.site.register(MediaFile)
