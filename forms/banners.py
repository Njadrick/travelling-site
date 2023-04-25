from kanisa.models import Banner
from kanisa.forms import KanisaBaseModelForm, BootstrapDateField
from kanisa.forms.widgets import (
    KanisaIntroInputWidget,
    KanisaThumbnailFileWidget
)


class BannerForm(KanisaBaseModelForm):
    publish_from = BootstrapDateField(required=False,
                                      help_text=('The date at which your '
                                                 'banner will become visible '
                                                 'on the website. If left '
                                                 'blank the start date is '
                                                 'unrestricted.'))
    publish_until = BootstrapDateField(required=False,
                                       help_text=('The final date on which '
                                                  'your banner will be '
                                                  'visible. If left blank '
                                                  'your banner will be '
                                                  'visible indefinitely.'))

    class Meta:
        exclude = ('visits', )
        model = Banner
        widgets = {'contents': KanisaIntroInputWidget(),
                   'image': KanisaThumbnailFileWidget(130, 90)}
