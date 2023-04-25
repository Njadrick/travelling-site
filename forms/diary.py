from collections import OrderedDict
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.core.urlresolvers import reverse
from django.forms.util import ErrorList
from kanisa.forms import (
    KanisaBaseModelForm,
    BootstrapTimeField,
    BootstrapDateField
)
from kanisa.forms.widgets import (
    KanisaMainInputWidget,
    KanisaTinyInputWidget,
    KanisaThumbnailFileWidget
)
from kanisa.models import (
    EventCategory,
    EventContact,
    RegularEvent,
    ScheduledEvent,
    ScheduledEventSeries
)


class EventContactForm(KanisaBaseModelForm):
    class Meta:
        model = EventContact
        widgets = {'image': KanisaThumbnailFileWidget(100, 100), }


class EventCategoryForm(KanisaBaseModelForm):
    class Meta:
        model = EventCategory


class ScheduledEventSeriesForm(KanisaBaseModelForm):
    class Meta:
        model = ScheduledEventSeries


class RegularEventForm(KanisaBaseModelForm):
    start_time = BootstrapTimeField()

    def __init__(self, *args, **kwargs):
        super(RegularEventForm, self).__init__(*args, **kwargs)

        if len(EventCategory.objects.all()) == 0:
            del self.fields['categories']

    class Meta:
        model = RegularEvent
        widgets = {'intro': KanisaTinyInputWidget(),
                   'details': KanisaMainInputWidget(),
                   'image': KanisaThumbnailFileWidget(100, 100), }


class ScheduledEventBaseForm(KanisaBaseModelForm):
    kanisa_form_class = 'scheduledevent'

    start_time = BootstrapTimeField()
    date = BootstrapDateField()
    end_date = BootstrapDateField(required=False)
    is_multi_day = forms.BooleanField(
        label='Multi-day event',
        required=False,
        help_text=('Check this box if this event spans multiple days.')
    )

    def __init__(self, *args, **kwargs):
        super(ScheduledEventBaseForm, self).__init__(*args, **kwargs)

        fields = OrderedDict()
        multi_day = self.fields.pop('is_multi_day')
        for key, value in self.fields.items():
            fields[key] = value
            if key == 'start_time':
                fields['is_multi_day'] = multi_day

        self.fields = fields

    def clean(self):
        super(ScheduledEventBaseForm, self).clean()
        cleaned_data = self.cleaned_data

        if cleaned_data['date']:
            sd = cleaned_data['date']
            ed = cleaned_data['end_date']
            multiday = cleaned_data['is_multi_day']

            if multiday:
                if not ed:
                    errors = ErrorList(['Multi-day events must have an end '
                                        'date'])
                    self._errors["is_multi_day"] = errors
                    del cleaned_data["is_multi_day"]

                if ed and ed < sd:
                    errors = ErrorList(['The event cannot end before it '
                                        'starts.'])
                    self._errors["end_date"] = errors
                    del cleaned_data["end_date"]

        return cleaned_data


class ScheduledEventEditForm(ScheduledEventBaseForm):
    class Meta:
        model = ScheduledEvent
        exclude = ('event', )
        widgets = {'details': KanisaMainInputWidget(), }


class ScheduledEventCreationForm(ScheduledEventBaseForm):
    event = forms.ModelChoiceField(queryset=RegularEvent.objects.
                                   order_by('title').all(),
                                   required=False)

    class Meta:
        model = ScheduledEvent
        widgets = {'details': KanisaMainInputWidget(), }


class RegularEventQueryForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()
    phone_number = forms.CharField(required=False)
    query = forms.CharField(
        required=False,
        widget=forms.Textarea,
        help_text=(
            'Any extra details you\'d like to give, or questions you\'d '
            'like answered.'
        ),
        label='Message',
    )
    event = forms.ModelChoiceField(
        queryset=RegularEvent.objects,
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super(RegularEventQueryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = reverse(
            'kanisa_public_diary_contact'
        )
        self.helper.add_input(
            Submit(
                'submit',
                'Send Query',
                css_class='btn-success'
            )
        )

    def set_event(self, event):
        self.initial['event'] = event
