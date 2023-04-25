from django.forms.util import ErrorList
from django import forms

from kanisa import conf
from kanisa.forms import KanisaBaseModelForm, BootstrapDateField
from kanisa.forms.widgets import (
    KanisaMainInputWidget,
    KanisaThumbnailFileWidget
)
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError, TIT2

from kanisa.models import (SermonSeries,
                           Sermon,
                           SermonSpeaker)


class SermonSeriesForm(KanisaBaseModelForm):
    class Meta:
        model = SermonSeries
        widgets = {'details': KanisaMainInputWidget(),
                   'image': KanisaThumbnailFileWidget(130, 130), }


class SermonSpeakerForm(KanisaBaseModelForm):
    class Meta:
        model = SermonSpeaker
        widgets = {'biography': KanisaMainInputWidget(), }


class SermonForm(KanisaBaseModelForm):
    date = BootstrapDateField()
    no_mp3 = forms.BooleanField(
        initial=False,
        required=False,
        widget=forms.HiddenInput
    )

    class Meta:
        model = Sermon
        widgets = {'details': KanisaMainInputWidget(),
                   'transcript': KanisaMainInputWidget()}

    def apply_id3(self, cleaned_data):
        try:
            audio = EasyID3(self.files['mp3'].temporary_file_path())
        except ID3NoHeaderError:
            audio = MP3(self.files['mp3'].temporary_file_path())
            audio["TIT2"] = TIT2(encoding=3, text=[cleaned_data['title']])
            audio.save()
            audio = EasyID3(self.files['mp3'].temporary_file_path())

        audio = EasyID3(self.files['mp3'].temporary_file_path())
        audio['title'] = cleaned_data['title']
        audio['artist'] = unicode(cleaned_data['speaker'])

        if not cleaned_data['series']:
            album_title = 'Sermons from %s' % conf.KANISA_CHURCH_NAME
        else:
            album_title = unicode(cleaned_data['series'])

        audio['album'] = album_title

        audio['albumartistsort'] = conf.KANISA_CHURCH_NAME
        audio['organization'] = conf.KANISA_CHURCH_NAME
        audio['genre'] = 'Speech'

        # Not sure if this date format is right - the MP3 players I've
        # got to test with don't show anything more than the year.
        if 'date' in cleaned_data:
            audio['date'] = cleaned_data['date'].strftime('%Y%m%d')

        audio.save()

    def clean(self):
        super(SermonForm, self).clean()
        cleaned_data = self.cleaned_data

        if 'mp3' in self.files:
            if hasattr(self.files['mp3'], 'temporary_file_path'):
                audio = MP3(self.files['mp3'].temporary_file_path())
            else:
                # You probably need to set FILE_UPLOAD_HANDLERS to
                # django.core.files.uploadhandler.TemporaryFileUploadHandler
                audio = None

            if audio is None or not audio.info or audio.info.sketchy:
                errors = ErrorList(['Please upload a valid MP3.'])
                self._errors["mp3"] = errors
                del cleaned_data["mp3"]
            else:
                self.apply_id3(cleaned_data)
        else:
            show_mp3_warning = not self.cleaned_data.get("no_mp3", False)
            if not self.instance.pk and show_mp3_warning:
                # We've got no MP3 file, and we've not seen this error
                # before - let's check that was intentional.
                self.data["no_mp3"] = True
                raise forms.ValidationError(
                    'No MP3 was uploaded - if that was intentional, please '
                    'click \'Save Sermon\' again.')

        return cleaned_data
