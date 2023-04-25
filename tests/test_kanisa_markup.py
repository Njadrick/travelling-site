from django.test import SimpleTestCase

from kanisa.templatetags.kanisa_markup import kanisa_markdown


class KanisaMarkupTest(SimpleTestCase):
    def test_basic(self):
        self.assertHTMLEqual(kanisa_markdown("hello"),
                             '<p>hello</p>')

    def test_newlines(self):
        self.assertHTMLEqual(kanisa_markdown("hello\nworld"),
                             '<p>hello<br>world</p>')
        self.assertHTMLEqual(kanisa_markdown("hello\n\nworld"),
                             '<p>hello</p><p>world</p>')

    def test_inline_image_that_does_not_exist(self):
        self.assertHTMLEqual(kanisa_markdown("hello ![img-99 headline]"),
                             '<p>hello ![img-99 headline]</p>')
