#  coding=utf-8
#
#  Author: Ernesto Arredondo Martinez (ernestone@gmail.com)
#  Created: 
#  Copyright (c)
from django.contrib.auth.forms import UserChangeForm, UsernameField
from django.forms import ModelForm

from .models import UserSample


class UserSampleCreationForm(ModelForm):

    class Meta:
        model = UserSample
        fields = ('email', 'countries')
        field_classes = {'username': UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs['autofocus'] = True

    def save(self, commit=True, **extra_args):
        user = super().save(commit=False)
        user.set_password(None)
        if commit:
            user.save()

        return user


class UserSampleChangeForm(UserChangeForm):
    class Meta:
        model = UserSample
        fields = ('email', 'countries', 'is_active', 'is_staff')
