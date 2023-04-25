from crispy_forms.layout import (
    Fieldset,
    Layout
)
from django import forms
from django.contrib.auth.models import Permission
from kanisa.forms import KanisaBaseForm
from kanisa.models import RegisteredUser
from .widgets import (
    KanisaInlineCheckboxes,
    KanisaThumbnailFileWidget
)


def get_choices():
    all_perms = Permission.objects.filter(content_type__app_label='kanisa')
    return [(p.codename, p.name) for p in all_perms
            if p.codename.startswith('manage')]


class UserUpdateForm(KanisaBaseForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()
    image = forms.FileField(widget=KanisaThumbnailFileWidget(100, 100),
                            required=False)
    permissions = forms.MultipleChoiceField(choices=get_choices(),
                                            label='',
                                            required=False)

    submit_text = 'Save Changes'

    def __init__(self, request_user, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)

        permissions_fieldset = Fieldset(
            'Permissions',
            KanisaInlineCheckboxes('permissions'),
        )

        if request_user.is_superuser:
            self.fields['administrator'] = forms.BooleanField(
                required=False,
                label='User is an administrator',
            )
            permissions_fieldset.fields.insert(0, 'administrator')

        self.helper.layout = Layout(
            Fieldset(
                'Profile',
                'first_name',
                'last_name',
                'email',
                'image',
            ),
            permissions_fieldset
        )


class UserCreateForm(UserUpdateForm):
    username = forms.RegexField(
        max_length=30,
        regex=r'^[\w.@+-]+$',
        help_text=("Required. 30 characters or fewer. Letters, digits and "
                   "@/./+/-/_ only."),
        error_messages={
            'invalid': ("This value may contain only letters, numbers and "
                        "@/./+/-/_ characters.")}
    )

    def __init__(self, request_user, *args, **kwargs):
        super(UserCreateForm, self).__init__(request_user, *args, **kwargs)

        # Add our username field to the layout
        self.helper.layout.fields[0].fields.insert(0, 'username')

    def clean_username(self):
        username = self.cleaned_data['username']

        try:
            RegisteredUser.objects.get(username=username)
        except RegisteredUser.DoesNotExist:
            return username

        raise forms.ValidationError(
            "A user with that username already exists."
        )
