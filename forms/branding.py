from django import forms
from kanisa.forms import KanisaBaseForm
from kanisa.utils.branding import get_available_colours
from PIL import Image


class BrandingForm(KanisaBaseForm):
    image = forms.FileField()
    submit_text = 'Update Image'

    def check_format(self, format):
        if format != self.expected_format:
            raise forms.ValidationError('The uploaded image must be '
                                        'a %s (the uploaded image '
                                        'was a %s).' % (self.expected_format,
                                                        format))

    def clean_image(self):
        data = self.cleaned_data['image']

        try:
            i = Image.open(self.files['image'].file)
        except IOError:
            raise forms.ValidationError('Please upload a valid image.')

        self.check_format(i.format)

        width, height = i.size

        self.check_size(width, height)

        return data


class LogoBrandingForm(BrandingForm):
    expected_format = 'JPEG'

    def __init__(self, *args, **kwargs):
        super(LogoBrandingForm, self).__init__(*args, **kwargs)
        self.fields['image'].help_text = ('Your site logo is used at the top '
                                          'of every page. It should be a JPEG '
                                          'exactly 85px high, and no wider '
                                          'than 500px.')

    def check_size(self, width, height):
        if height < 85:
            raise forms.ValidationError('The uploaded image must be at least '
                                        '85px high (the uploaded image was '
                                        '%s%s).' % (height, 'px'))


class SeasonalBrandingForm(BrandingForm):
    expected_format = 'JPEG'

    def __init__(self, *args, **kwargs):
        super(SeasonalBrandingForm, self).__init__(*args, **kwargs)
        self.fields['image'].help_text = (
            'The seasonal header is used at the top of Christmas and Easter '
            'pages.'
        )

    def check_size(self, width, height):
        if height < 140:
            raise forms.ValidationError(
                'The uploaded image must be at least 140px high (the uploaded '
                'image was %s%s).' % (height, 'px')
            )


class AppleBrandingForm(BrandingForm):
    expected_format = 'JPEG'

    def __init__(self, *args, **kwargs):
        super(AppleBrandingForm, self).__init__(*args, **kwargs)
        self.fields['image'].help_text = (
            'The Apple icon needs to be at least 144px by 144px. This will be '
            'scaled down for non-retina devices to 72px by 72px.'
        )

    def check_size(self, width, height):
        if height != width:
            raise forms.ValidationError('The uploaded image must be exactly '
                                        'square (the uploaded image was '
                                        '%s by %s).' % (width, height))

        if height < 144:
            raise forms.ValidationError('The uploaded image must be at least '
                                        '144px high (the uploaded image was '
                                        '%s%s).' % (height, 'px'))


class FaviconBrandingForm(BrandingForm):
    expected_format = 'PNG'

    def __init__(self, *args, **kwargs):
        super(FaviconBrandingForm, self).__init__(*args, **kwargs)
        self.fields['image'].help_text = ('This should be a PNG file '
                                          'exactly 32px by 32px.')

    def check_size(self, width, height):
        if height != width:
            raise forms.ValidationError('The uploaded image must be exactly '
                                        'square (the uploaded image was '
                                        '%s by %s).' % (width, height))

        if height != 32:
            raise forms.ValidationError('The uploaded image must be exactly '
                                        '32px high (the uploaded image was '
                                        '%s%s).' % (height, 'px'))


class BrandingColoursForm(KanisaBaseForm):
    submit_text = 'Update Colours'

    def __init__(self, *args, **kwargs):
        colours = get_available_colours()

        for name, info in colours.items():
            field = forms.RegexField(regex='^#([0-9a-fA-F]{6})$',
                                     help_text=info)
            self.base_fields[name] = field

        super(BrandingColoursForm, self).__init__(*args, **kwargs)
