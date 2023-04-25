from kanisa.forms import KanisaBaseModelForm
from kanisa.forms.widgets import KanisaMainInputWidget
from kanisa.models import Document


class DocumentForm(KanisaBaseModelForm):
    class Meta:
        model = Document
        widgets = {'details': KanisaMainInputWidget(), }


class DocumentFormSimple(KanisaBaseModelForm):
    class Meta:
        model = Document
        exclude = ('details', 'public', )
