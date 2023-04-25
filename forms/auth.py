from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm
)
from kanisa.forms import (
    KanisaBaseModelForm,
    KanisaPrettyForm
)
from kanisa.forms.widgets import KanisaThumbnailFileWidget
from password_reset.forms import PasswordRecoveryForm, PasswordResetForm


class KanisaLoginForm(KanisaPrettyForm, AuthenticationForm):
    submit_text = 'Login'

    def __init__(self, *args, **kwargs):
        self.helper = self.get_form_helper()
        super(KanisaLoginForm, self).__init__(*args, **kwargs)


class KanisaChangePasswordForm(KanisaPrettyForm, PasswordChangeForm):
    submit_text = 'Change Password'

    def __init__(self, *args, **kwargs):
        self.helper = self.get_form_helper()
        super(KanisaChangePasswordForm, self).__init__(*args, **kwargs)


class KanisaAccountCreationForm(KanisaPrettyForm, UserCreationForm):
    submit_text = 'Register'

    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(help_text=('We\'ll need an email address to get '
                                        'in touch with you to verify your '
                                        'account.'))

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'first_name', 'last_name', )

    def __init__(self, *args, **kwargs):
        self.helper = self.get_form_helper()
        super(KanisaAccountCreationForm, self).__init__(*args, **kwargs)

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

    def save(self, commit=True):
        user = super(KanisaAccountCreationForm, self).save(commit)
        user.is_active = False
        user.save()
        return user


class KanisaPasswordRecoveryForm(KanisaPrettyForm, PasswordRecoveryForm):
    submit_text = 'Recover my password'

    def __init__(self, *args, **kwargs):
        self.helper = self.get_form_helper()
        super(KanisaPasswordRecoveryForm, self).__init__(*args, **kwargs)


class KanisaPasswordResetForm(KanisaPrettyForm, PasswordResetForm):
    submit_text = 'Reset my password'

    def __init__(self, *args, **kwargs):
        self.helper = self.get_form_helper()
        super(KanisaPasswordResetForm, self).__init__(*args, **kwargs)


class KanisaAccountModificationForm(KanisaBaseModelForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()
    image = forms.FileField(widget=KanisaThumbnailFileWidget(100, 100))

    submit_text = 'Save Changes'

    def add_save_and_continue(self):
        pass

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email', 'image', ]
