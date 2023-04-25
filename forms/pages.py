from kanisa.forms import KanisaBaseModelForm
from kanisa.forms.widgets import (
    KanisaIntroInputWidget,
    KanisaMainInputWidget
)
from kanisa.models import Page


class PageForm(KanisaBaseModelForm):
    class Meta:
        model = Page
        widgets = {'lead': KanisaIntroInputWidget(),
                   'contents': KanisaMainInputWidget(), }
