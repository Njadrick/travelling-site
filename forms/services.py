from django import forms
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from crispy_forms.layout import Layout, HTML
from kanisa.forms import (
    BootstrapDateField,
    KanisaBaseForm,
    KanisaBaseModelForm
)
from kanisa.forms.fields import (
    AccountChoiceField,
    MultipleAccountChoiceField
)
from kanisa.models import (
    Song,
    Service,
    ScheduledEvent,
    Composer,
    Band
)


class AddSongToServiceForm(KanisaBaseForm):
    song = forms.ModelChoiceField(queryset=Song.objects.all())
    submit_text = 'Add Song'


class SongForm(KanisaBaseModelForm):
    def get_form_helper(self):
        helper = super(SongForm, self).get_form_helper()
        helper.layout = Layout(
            'title',
            'composers',
            HTML('{% include '
                 '"kanisa/members/services/_composer_add.html" '
                 '%}'),
        )
        return helper

    class Meta:
        model = Song


class MergeSongForm(KanisaBaseForm):
    other_songs = forms.ModelMultipleChoiceField(
        queryset=Song.objects.all(),
    )
    submit_text = 'Merge songs'

    def __init__(self, target_song, *args, **kwargs):
        super(MergeSongForm, self).__init__(*args, **kwargs)
        qs = self.fields['other_songs'].queryset.exclude(
            pk=target_song.pk
        )
        self.fields['other_songs'].queryset = qs


class CreateSongForm(SongForm):
    submit_text = 'Create Song'


class UpdateSongForm(SongForm):
    submit_text = 'Save Song'


class EventChoiceField(forms.ModelChoiceField):
    # This is only used when the field is hidden, and is designed to
    # make the view a bit faster to render.
    def label_from_instance(self, obj):
        return obj.pk


class ServiceForm(KanisaBaseModelForm):
    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)

        if self.instance.pk:
            del self.fields['event']
            del self.fields['date']
            del self.fields['band']
        else:
            url = reverse('kanisa_xhr_bandinformation')
            self.helper.attrs["data-band-info-url"] = url
            url = reverse('kanisa_xhr_eventinformation')
            self.helper.attrs["data-event-info-url"] = url

    date = BootstrapDateField()
    # The list of events in the field events is largely ignored. We
    # need to specify .all() to ensure that any event which is
    # selected (after the user has selected a date) is accepted. With
    # ScheduledEvent.objects.none(), the view renders more quickly,
    # but no events are accepted when the user hits submit.
    event = EventChoiceField(ScheduledEvent.bare_objects.all())
    band = forms.ModelChoiceField(Band.objects.all(), required=False)
    band_leader = AccountChoiceField(get_user_model().objects.all())
    musicians = MultipleAccountChoiceField(
        get_user_model().objects.all(),
        required=False
    )

    class Meta:
        fields = ('date', 'event', 'band', 'band_leader', 'musicians', )
        model = Service


class ComposerForm(KanisaBaseModelForm):
    class Meta:
        model = Composer


class BandForm(KanisaBaseModelForm):
    band_leader = AccountChoiceField(get_user_model().objects.all())
    musicians = MultipleAccountChoiceField(
        get_user_model().objects.all(),
        required=False
    )

    class Meta:
        model = Band
