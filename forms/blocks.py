from django import forms
from kanisa.forms import KanisaBaseModelForm
from kanisa.forms.widgets import KanisaMainInputWidget
from kanisa.models import Block


class BlockForm(KanisaBaseModelForm):
    referer = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Block
        widgets = {'contents': KanisaMainInputWidget(), }
        fields = ('contents', 'referer', )
