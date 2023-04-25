from django.test import TestCase
from kanisa.models import InlineImage
import factory


class InlineImageFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'InlineImage Title #%d' % n)
    image = 'non_existent_image.jpg'

    class Meta:
        model = InlineImage


class InlineImageTest(TestCase):
    def test_unicode(self):
        inline_image = InlineImageFactory.build()
        self.assertEqual(unicode(inline_image), 'InlineImage Title #0')
