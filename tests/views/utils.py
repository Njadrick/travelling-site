from django.contrib.auth.models import AnonymousUser
from tests.utils import KanisaViewTestCase


class XHRBaseTestCase(KanisaViewTestCase):
    def get_request(self):
        request = super(XHRBaseTestCase, self).get_request()
        request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        return request

    def test_xhr_only(self):
        if type(self) == XHRBaseTestCase:
            return

        request = self.get_request()
        del request.META['HTTP_X_REQUESTED_WITH']

        resp = self.fetch_from_factory(request)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.content,
                         'This page is not directly accessible.')

    def test_correct_method_only(self):
        if type(self) == XHRBaseTestCase:
            return

        if self.method == 'get':
            resp = self.client.post(self.url)
        elif self.method == 'post':
            resp = self.client.get(self.url)

        self.assertEqual(resp.status_code, 405)
        self.assertEqual(resp.content,
                         '')

    def test_must_be_authenticated(self):
        if type(self) == XHRBaseTestCase:
            return

        if not hasattr(self, 'permission_text'):
            return

        request = self.get_request()
        request.user = AnonymousUser()
        resp = self.fetch_from_factory(request)
        self.assertEqual(resp.status_code, 403)
