from django import forms
from django.contrib.auth import get_user_model
from kanisa.forms import KanisaBaseModelForm, BootstrapDateField
from kanisa.forms.fields import AccountChoiceField
from kanisa.forms.widgets import (
    KanisaBlogTeaserInputWidget,
    KanisaMainInputWidget,
)
from kanisa.models import BlogPost, BlogComment


class BlogPostForm(KanisaBaseModelForm):
    author = AccountChoiceField(
        get_user_model().objects.all(),
        required=False
    )
    publish_date = BootstrapDateField(
        help_text=('Blog posts are published on the site at 00:00 on the '
                   'publish date.')
    )

    class Meta:
        model = BlogPost
        widgets = {
            'main_text': KanisaMainInputWidget(),
            'teaser_text': KanisaBlogTeaserInputWidget(),
        }


class BlogCommentForm(KanisaBaseModelForm):
    submit_text = 'Post comment'

    def get_form_helper(self):
        helper = super(BlogCommentForm, self).get_form_helper()
        helper.form_show_labels = False
        return helper

    class Meta:
        model = BlogComment
        fields = ['body', ]
        widgets = {
            'body': forms.Textarea(attrs={'rows': 4}),
        }
