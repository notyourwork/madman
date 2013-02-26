from django import forms
from django.contrib.auth.models import User
from django.conf import settings 
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm
from madman.models import UserProfile

class UserProfileForm( ModelForm ):
    class Meta:
        model = UserProfile 
        exclude = (
            'user', 
        )
    email = forms.EmailField(
        label=_("Email"), 
        help_text=_("User Email")
    )
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        try:
            self.fields['email'].initial = self.instance.user.email 
        except User.DoesNotExist:
            pass
    
    def save(self, *args, **kwargs):
        user = self.instance.user 
        email = self.cleaned_data['email']
        user.save() 
        profile = super(UserProfileForm, self).save(*args, **kwargs)
        return profile


