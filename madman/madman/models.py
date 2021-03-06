from django.db import models
import os, fnmatch, stat, mimetypes, datetime, re 
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from madman import audit 
from madman import utility 
from django.db.models.signals import post_save
from django.contrib.auth.models import User

import logging 
logger = logging.getLogger(__name__) 

#class BaseCommentAbstractModel(models.Model):
#    """
#    An abstract base class that any custom comment models probably should
#    subclass.
#    """
#
#    # Content-object field
#    content_type   = models.ForeignKey(ContentType,
#            verbose_name=_('content type'),
#            related_name="content_type_set_for_%(class)s")
#    object_pk      = models.TextField(_('object ID'))
#    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")
#
#    # Metadata about the comment
#    site        = models.ForeignKey(Site)
#
#    class Meta:
#       abstract = True
#
#    def get_content_object_url(self):
#        """
#        Get a URL suitable for redirecting to the content object.
#        """
#        return urlresolvers.reverse(
#            "comments-url-redirect",
#            args=(self.content_type_id, self.object_pk)
#        )

class BasicMediaModel( models.Model ):
    #    name = models.CharField( max_length=255, db_index=True, unique=True )
    created_time = models.DateTimeField("Created Date", blank=True, null=True )
    updated_time = models.DateTimeField("Updated Date", blank=True, null=True )
    accessed_time = models.DateTimeField("Accessed Date", blank=True, null=True )
    scraped_time = models.DateTimeField("Scraped Date", blank=True, null=True )
    class Meta:
        abstract = True
    
class MediaType( BasicMediaModel ):
    name = models.CharField( max_length=255, db_index=True, unique=True )
    types = models.ManyToManyField('self', null=True, symmetrical=False)
    definition = models.CharField(max_length=255, db_index=True, blank=True )
    class Meta:
        verbose_name = _('Media Type')
        verbose_name_plural = _('Media Types')
        get_latest_by = "name"
    def __unicode__( self ):
        return self.name
    @models.permalink
    def get_absolute_url( self ):
        return ('mediatype', (), { 'id': self.pk })
    def get_named_url( self ):
        return self.name 
    def get_locations( self ):
        return MediaLocation.objects.filter(location_type=self.pk, parent=None)    

class MediaLocation( BasicMediaModel ):
    name = models.CharField(
        "Location Name", 
        max_length=255, 
        db_index=True
    )
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL )
    full_path = models.CharField(
        max_length=255, 
        blank=True, 
        null=True 
    ) 
    path = models.CharField(
        max_length=255, 
        blank=True, 
        null=True 
    ) 
    location_type = models.ForeignKey(MediaType, null=True, blank=True, on_delete=models.SET_NULL )
    history = audit.AuditTrail() 
    size = models.CharField( 
        "Location Size", 
        max_length=50, 
        blank=True, 
        null=True 
    )
    class Meta:
        get_latest_by = "created_time"
    def __unicode__(self):
        return self.name
    def save(self, *args, **kwargs):
        (head, tail) = os.path.split(self.path) 
        if tail == '':
            self.name = head 
        else: 
            self.name = tail
        self.size = self.get_size() 
        #if this type is empty and parent is defined 
        #use parent for media type 
        if not self.location_type: 
            if self.parent:
                self.location_type = self.parent.get_type()
            else:
                self.location_type = utility.get_type( self.get_path() )
        super(MediaLocation, self).save(*args, **kwargs) 
    def location_filter( self, item ):
        excludes = ['lost+found', '.DS_STORE', '.Trash-500', 'All-files-CRC-OK' ]
        if not item in excludes:
            return item
    @models.permalink
    def get_absolute_url( self ):
        return ('medialocation', (), { 'id': self.pk })
    def get_named_url( self ):
        return "/place/%s/" % self.name.replace(" ", "-") 
    def get_type( self ):
        return self.location_type
    def is_parent( self ):
        if self.parent:
            return False
        else:
            return True 
    def get_fullname( self ):
        if self.parent:
            return "%s -> %s" % (self.parent.get_fullname(), self.name) 
        else:
            return self.name
    def get_path( self ):
        if self.parent:
            new_path = self.path 
            if self.path[0:1] == '/':
                new_path = self.path[1:]
            return os.path.join( self.parent.get_path(), new_path) 
        else:
            return self.path
    def print_size( self ):
        return utility.humanize_bytes( self.size )
    def get_size( self ):
        return utility.get_dir_size( self.get_path() )
    def find( self ):  
        found = []
        try:  
            for item in filter(self.location_filter, os.listdir( self.full_path )):
                full_path = os.path.join( self.full_path, item )
                logger.info( "self.full_path=%s\nitem=%s" % (full_path, item,) )
                if os.path.isdir( full_path ):
                    #store media location, and find media if created  
                    location, created = MediaLocation.objects.get_or_create(name="%s" % item, path="%s" % item, full_path=full_path, parent=self)
                    if created:
                        found.append(location)  
                        found.extend(location.find())
                elif os.path.isfile(full_path) and not os.path.islink( full_path):
                    #store media file or 
                    f, created = MediaFile.objects.get_or_create( name="%s" % item, location=self, size=utility.get_size(full_path) ) 
                    if created: 
                        found.append( f ) 
                elif os.path.islink( full_path ) and os.path.exists( fullname ):
                        link, created = MediaLink.objects.get_or_create( name=tail, location=self, comments=os.readlink(fullname) )
        except:
            logger.error( "self.full_path=%s\nitem=%s" % (full_path, item,) )
            return found 
        return found

class MediaFile( BasicMediaModel ):
    """A file object stored on some device."""
    name = models.CharField("MediaFile Name", max_length=255, db_index=True)
    location = models.ForeignKey(
        MediaLocation, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL
    )
    file_type = models.ForeignKey( MediaType, blank=True, null=True )
    size = models.BigIntegerField("Size of MediaFile",default=0 )
    history = audit.AuditTrail()
    class Meta:
        get_latest_by = "created_time"
    def __unicode__(self):
        return self.name
    def get_path( self ):
        return ("%s/%s" % (self.location.get_path(), self.name) )
    def get_fullname( self ):
        if self.location:
            return "%s -> %s" % (self.location.get_fullname(), self.name) 
        else:
            return self.name
    def get_real_size( self ):
        try: 
            size = os.path.getsize( self.get_path() )
        except OSError:
            size = 0
        return utility.humanize_bytes( size )
    def get_size( self ):
        return self.size
    def print_size( self ):
        return utility.humanize_bytes( self.size )
    def get_location( self ):
        return self.location
    @models.permalink
    def get_absolute_url(self):
        return ('mediafile', (), { 'id': self.pk }) 

class MediaLink( BasicMediaModel ):
    """Object for representing symlinks and their
    relation to locations/files they represent.
    
    name: The link which resides in self.location
    location: the location where this link lives 
    mediafile: if set is the mediafile this link references
    (mediafile or medialocation will be set, not both.) 
    """
    name = models.CharField("Link name",max_length=255,db_index=True)
    location = models.ForeignKey(
        MediaLocation,
        null=True,
        blank=True,
    )
    mediafile = models.ForeignKey(
        MediaFile,
        null=True,
        blank=True,
    )
    comments = models.TextField() 
    def __unicode__(self):
        return self.name
    def get_link_path( self ):
        return ("%s/%s" % (self.location.get_path(), self.name) )
    def get_file_path( self ):
        return "%s" % (self.mediafile.get_path(), )

class UserProfile(models.Model):
    '''an extension on pybb userprofile for storing batter
    specific account information'''
    user = models.OneToOneField(User)
    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
    def __unicode__(self):
        return self.user.username
    @models.permalink
    def get_absolute_url(self):
        return (
            'profiles_profile_detail', 
            (), 
            { 'username': self.user.username }
        )
    @models.permalink
    def get_edit_url(self):
        return ('profiles_edit_profile', )
    def get(self):
        '''return a list of field, value tuples
        for this object, can be used in a template
        when dealing with a queryset to iterate over
        all data in each object in the queryset'''
        return [(field, field.value_to_string(self)) for field in UserProfile._meta.fields]
    def save(self, *args, **kwargs):
        super(UserProfile, self).save(*args, **kwargs) 


#save UserProfile when saving User object 
def user_saved(instance, created, *args, **kwargs):
    '''create a profile for any created users'''
    if created:
        UserProfile.objects.get_or_create(user=instance)

post_save.connect(user_saved, sender=User)

