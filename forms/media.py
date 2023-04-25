from kanisa.forms import KanisaBaseModelForm
from kanisa.forms.widgets import KanisaThumbnailFileWidget
from kanisa.models import InlineImage


class InlineImageForm(KanisaBaseModelForm):
    class Meta:
        model = InlineImage
        widgets = {'image': KanisaThumbnailFileWidget(180, 180), }
