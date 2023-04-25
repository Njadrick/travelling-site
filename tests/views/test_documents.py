from django.core.urlresolvers import reverse
from tests.utils import KanisaViewTestCase


class DocumentManagementViewTest(KanisaViewTestCase):
    def test_views_protected(self):
        self.view_is_restricted(reverse('kanisa_manage_documents'))
        self.view_is_restricted(reverse('kanisa_manage_documents_create'))

        # These would 404 if you were logged in
        self.view_is_restricted(reverse('kanisa_manage_documents_update',
                                        args=[1, ]))
        self.view_is_restricted(reverse('kanisa_manage_documents_delete',
                                        args=[1, ]))
