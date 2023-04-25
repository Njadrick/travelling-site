from django.core.urlresolvers import reverse
from tests.utils import KanisaViewTestCase


class ManagementViewTest(KanisaViewTestCase):
    def test_views_protected(self):
        self.view_is_restricted(reverse('kanisa_manage_index'))

    def test_root_view(self):
        url = reverse('kanisa_manage_index')
        self.client.login(username='fred', password='secret')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'kanisa/management/index.html')
