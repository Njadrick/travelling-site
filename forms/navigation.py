from kanisa.forms import KanisaBaseModelForm
from kanisa.models import NavigationElement


class NavigationElementForm(KanisaBaseModelForm):
    class Meta:
        model = NavigationElement
