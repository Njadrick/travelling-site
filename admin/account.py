from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import (
    UserChangeForm,
    UserCreationForm,
)
from django.utils.translation import ugettext_lazy as _
from kanisa.conf import KANISA_ADMIN_THUMBS_SIZE
from kanisa.models import RegisteredUser
from sorl.thumbnail import default


class RegisteredUserCreationForm(UserCreationForm):
    class Meta:
        model = RegisteredUser
        fields = ("username",)

    def clean_username(self):
        # This shouldn't be necessary, but currently (as of Django
        # 1.6) is. See bit.ly/1dxSdib, and
        # https://code.djangoproject.com/ticket/19353
        username = self.cleaned_data['username']
        try:
            self._meta.model._default_manager.get(username=username)
        except self._meta.model.DoesNotExist:
            return username

        raise forms.ValidationError(
            self.error_messages['duplicate_username']
        )


class RegisteredUserChangeForm(UserChangeForm):
    class Meta:
        model = RegisteredUser
        fields = (
            'username',
            'password',
            'first_name',
            'last_name',
            'email',
            'image',
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions',
            'last_login',
            'date_joined',
            'is_spam',
        )


class RegisteredUserAdmin(UserAdmin):
    form = RegisteredUserChangeForm
    add_form = RegisteredUserCreationForm

    list_display = (
        'username',
        'image_thumb',
        'first_name',
        'last_name',
        'created',
    )

    search_fields = (
        'username',
        'first_name',
        'last_name',
        'email',
    )

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email',
                                         'image')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'is_spam', 'groups',
                                       'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super(RegisteredUserAdmin,
                     self).get_form(request, obj, **kwargs)

        if obj is not None:
            form.base_fields['first_name'].required = True
            form.base_fields['last_name'].required = True
            form.base_fields['email'].required = True

        return form

    def image_thumb(self, obj):
        if obj.image:
            thumb = default.backend.get_thumbnail(obj.image.file,
                                                  KANISA_ADMIN_THUMBS_SIZE)
            return u'<img width="%s" height="%s" src="%s" />' % (thumb.width,
                                                                 thumb.height,
                                                                 thumb.url)
        return "No Image"
    image_thumb.short_description = 'Image'
    image_thumb.allow_tags = True

admin.site.register(RegisteredUser, RegisteredUserAdmin)
