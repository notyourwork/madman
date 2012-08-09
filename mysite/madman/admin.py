from madman.models import *
from django.contrib import admin 
from mptt.admin import MPTTModelAdmin


class MediaTypeAdmin( admin.ModelAdmin ):
    fieldsets = [
        (None, {'fields':  ['name', 'types', 'definition',]}), 
        ('Dates', {'fields': ['created_time', 'updated_time', 'accessed_time', 'scraped_time']}), 
    ]
    list_display = ('name', 'definition') 
    
class MediaLocationAdmin( admin.ModelAdmin ):
    fieldsets = [
        (None, {'fields': ['name', 'parent', 'path', 'location_type', 'size' ]}), 
        #('Dates', {'fields': ['created', 'updated',  'scraped']}), 
    ]
    list_display = ('name', 'path', 'get_path', 'is_parent', 'get_fullname' ) 
    search_fields = ['name', 'path',]

class MediaFileAdmin( admin.ModelAdmin ):
    fieldsets = [
        (None, {'fields': ['name']}),
        ('Attributes', {'fields': ['location', 'size']}),
        #('Dates', {'fields': ['created_time', 'updated_time', 'scraped_time', 'accessed_time'], 'classes': ['collapse']}),
    ]
    list_display = ('name', 'get_size', 'location', 'get_fullname')

class MediaTreeAdmin( admin.ModelAdmin ):
    fieldsets = [
        (None, {'fields': ['name', 'mediatype', 'parent', ]}), 
    ]
    list_display = ('name', 'mediatype', 'parent')
    search_fields = ['name', 'mediatype', 'parent']

class MediaLinkAdmin( admin.ModelAdmin ):
    fieldsets = [
        (None, {'fields': ['name', 'mediafile', 'location', 'comments' ]}), 
    ]
    list_display = ('name', 'mediafile', 'location', 'comments')
    search_fields = ['name', 'mediafile', 'location']
admin.site.register(UserProfile) 
admin.site.register(MediaTree, MPTTModelAdmin)
admin.site.register(MediaType, MediaTypeAdmin)
admin.site.register(MediaLink, MediaLinkAdmin)
admin.site.register(MediaLocation, MediaLocationAdmin)
admin.site.register(MediaFile, MediaFileAdmin)
