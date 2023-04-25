from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings
from kanisa.models import Page
from tests.utils import KanisaViewTestCase
import factory


class PageFactory(factory.DjangoModelFactory):
    title = 'Page Title'

    class Meta:
        model = Page


class PageManagementViewTest(KanisaViewTestCase):
    def test_views_protected(self):
        self.view_is_restricted(reverse('kanisa_manage_pages'))
        self.view_is_restricted(reverse('kanisa_manage_pages_create'))

        # This would 404 if you were logged in
        self.view_is_restricted(reverse('kanisa_manage_pages_update',
                                        args=[1, ]))

    def test_index_view(self):
        self.client.login(username='fred', password='secret')
        resp = self.client.get(reverse('kanisa_manage_pages'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'kanisa/management/pages/index.html')
        self.client.logout()

    def test_create_page_view(self):
        self.client.login(username='fred', password='secret')

        url = reverse('kanisa_manage_pages_create')

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'kanisa/management/create.html')

        # Should 404 with an invalid ID
        resp = self.client.get(url + '?parent=foo')
        self.assertEqual(resp.status_code, 404)

        # Should 404 with a valid ID, which is non-existent
        resp = self.client.get(url + '?parent=99')
        self.assertEqual(resp.status_code, 404)

        pk = PageFactory.create().pk
        resp = self.client.get(url + '?parent=%s' % pk)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['form'].initial['parent'].pk, 1)

        resp = self.client.post(url, {'title': "Test page"},
                                follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('messages' in resp.context)
        self.assertEqual([m.message for m in resp.context['messages']],
                         [u'Page "Test page" created.', ])

        self.client.logout()

    def test_delete_page_view(self):
        parent_page = PageFactory.create(title="About Us")
        child_page = PageFactory.create(parent=parent_page,
                                        title="Staff")
        child_page2 = PageFactory.create(parent=parent_page,
                                         title="Location")

        self.client.login(username='fred', password='secret')

        # Can't delete pages which aren't root nodes - getting the
        # confirmation page should 404.
        resp = self.client.get(reverse('kanisa_manage_pages_delete',
                                       args=[parent_page.pk, ]))
        self.assertEqual(resp.status_code, 404)

        # So should running the actual delete.
        resp = self.client.post(reverse('kanisa_manage_pages_delete',
                                        args=[1, ]),
                                {})
        self.assertEqual(resp.status_code, 404)

        resp = self.client.get(reverse('kanisa_manage_pages_delete',
                                       args=[child_page.pk, ]))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post(reverse('kanisa_manage_pages_delete',
                                        args=[child_page.pk, ]),
                                {},
                                follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertTrue('messages' in resp.context)
        self.assertEqual([m.message for m in resp.context['messages']],
                         [u'Staff deleted.', ])

        resp = self.client.post(reverse('kanisa_manage_pages_delete',
                                        args=[child_page2.pk, ]),
                                {},
                                HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, '"Location" deleted')

        self.client.logout()

    def test_update_page_view(self):
        parent_page = PageFactory.create(title="About Us")
        child_page = PageFactory.create(title="Child page",
                                        parent=parent_page)
        self.client.login(username='fred', password='secret')

        p = Page.objects.get(pk=parent_page.pk)
        url = reverse('kanisa_manage_pages_update', args=[1, ])

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post(url, {'title': p.title,
                                      'contents': p.contents},
                                follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('messages' in resp.context)
        self.assertEqual([m.message for m in resp.context['messages']],
                         [u'Page "%s" saved.' % p.title, ])

        # Pages cannot be their own parents
        resp = self.client.post(url, {'title': p.title,
                                      'contents': p.contents,
                                      'parent': p.pk})
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp, 'form', 'parent',
                             'A page cannot be its own parent.')

        # Pages cannot have their descendants as their parent
        resp = self.client.post(url, {'title': p.title,
                                      'contents': p.contents,
                                      'parent': child_page.pk})
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp, 'form', 'parent',
                             'Invalid parent - cyclical hierarchy detected.')

        url = reverse('kanisa_manage_pages_update', args=[child_page.pk, ])
        resp = self.client.post(url, {'title': child_page.title,
                                      'contents': child_page.contents,
                                      'parent': parent_page.pk})
        self.assertEqual(resp.status_code, 302)

        self.client.logout()


class PagePublicViewTest(TestCase):
    @override_settings(APPEND_SLASH=True)
    def test_root_view_without_trailing_slash_append_slash_on(self):
        PageFactory.create(title="About Us")
        response = self.client.get('/about-us')
        self.assertRedirects(response, '/about-us/', 301)

    @override_settings(APPEND_SLASH=False)
    def test_root_view_without_trailing_slash_append_slash_off(self):
        PageFactory.create(title="About Us")
        response = self.client.get('/about-us')
        self.assertEqual(response.status_code, 404)

    def test_root_view_with_trailing_slash(self):
        parent_page = PageFactory.create(title="About Us")
        response = self.client.get('/about-us/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page'], parent_page)

    def test_child_view(self):
        parent_page = PageFactory.create(title="About Us")
        child_page = PageFactory.create(title="Staff", parent=parent_page)
        response = self.client.get('/about-us/staff/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page'], child_page)

    def test_non_existent_page(self):
        PageFactory.create(title="About Us")
        response = self.client.get('/about-uss/')
        self.assertEqual(response.status_code, 404)
