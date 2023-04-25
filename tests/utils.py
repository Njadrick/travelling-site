from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.urlresolvers import reverse, reverse_lazy
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings


class KanisaViewTestCase(TestCase):
    def setUp(self):
        self.bob = get_user_model().objects.create_user('bob', '', 'secret')
        self.bob.email = 'bob@example.com'
        self.bob.is_staff = False
        self.bob.save()

        self.fred = get_user_model().objects.create_user('fred', '', 'secret')
        p = Permission.objects.get(codename='manage_banners')
        self.fred.user_permissions.add(p)
        p = Permission.objects.get(codename='manage_diary')
        self.fred.user_permissions.add(p)
        p = Permission.objects.get(codename='manage_sermons')
        self.fred.user_permissions.add(p)
        p = Permission.objects.get(codename='manage_users')
        self.fred.user_permissions.add(p)
        p = Permission.objects.get(codename='manage_pages')
        self.fred.user_permissions.add(p)
        p = Permission.objects.get(codename='manage_navigation')
        self.fred.user_permissions.add(p)
        p = Permission.objects.get(codename='manage_services')
        self.fred.user_permissions.add(p)
        self.fred.email = 'fred@example.com'

        self.fred.save()

        self.superman = get_user_model().objects.create_user('superman',
                                                             '', 'secret')
        self.superman.is_superuser = True
        self.superman.save()

        self.factory = RequestFactory()

    @override_settings(LOGIN_URL=reverse_lazy('kanisa_members_login'))
    def view_is_restricted(self, url):
        # Not logged in
        resp = self.client.get(url)
        login_url = reverse('kanisa_members_login')
        self.assertRedirects(resp, '%s?next=%s' % (login_url, url),
                             302, 200)

        # Logged in as non-staff member
        self.client.login(username='bob', password='secret')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)
        self.client.logout()

    def fetch_from_factory(self, request, params={}, **kwargs):
        if self.method == 'post':
            request.POST = params
        elif self.method == 'get':
            request.GET = params

        return self.view.as_view()(request, **kwargs)

    def get_request(self):
        if self.method == 'post':
            request = self.factory.post(self.url)
        else:
            request = self.factory.get(self.url)

        request.session = {}
        return request
