from django.core.urlresolvers import reverse
from kanisa.models import NavigationElement
from tests.utils import KanisaViewTestCase
import factory


class NavigationElementFactory(factory.DjangoModelFactory):
    title = 'NavigationElement Title'

    class Meta:
        model = NavigationElement


class NavigationManagementViewTest(KanisaViewTestCase):
    def test_views_protected(self):
        self.view_is_restricted(reverse('kanisa_manage_navigation'))
        self.view_is_restricted(reverse('kanisa_manage_navigation_create'))

        # This would 404 if you were logged in
        self.view_is_restricted(reverse('kanisa_manage_navigation_update',
                                        args=[1, ]))

    def test_index_view(self):
        self.client.login(username='fred', password='secret')
        resp = self.client.get(reverse('kanisa_manage_navigation'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,
                                'kanisa/management/navigation/index.html')
        self.client.logout()

    def test_create_navigation_view(self):
        self.client.login(username='fred', password='secret')

        url = reverse('kanisa_manage_navigation_create')

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'kanisa/management/create.html')

        self.client.logout()

    def test_navigation_element_move_views(self):
        def refresh(nav):
            return NavigationElement.objects.get(pk=nav.pk)

        first = NavigationElementFactory.create(title="ABC")
        second = NavigationElementFactory.create(title="XYZ")

        self.client.login(username='fred', password='secret')

        url = reverse('kanisa_manage_navigation_move_down', args=[first.pk, ])

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)

        self.assertEqual([n.pk for n in NavigationElement.objects.all()],
                         [second.pk, first.pk, ])

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

        url = reverse('kanisa_manage_navigation_move_up', args=[first.pk, ])

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)

        self.assertEqual([n.pk for n in NavigationElement.objects.all()],
                         [first.pk, second.pk, ])

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

        self.client.logout()

    def test_navigation_delete_view(self):
        first = NavigationElementFactory.create(title="ABC")
        second = NavigationElementFactory.create(title="XYZ", parent=first)

        self.client.login(username='fred', password='secret')

        # Can't delete non-leaf nodes
        url = reverse('kanisa_manage_navigation_delete', args=[first.pk, ])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 404)

        url = reverse('kanisa_manage_navigation_delete', args=[second.pk, ])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)

        self.assertEqual([n.pk for n in NavigationElement.objects.all()],
                         [first.pk, ])

        # Can no delete the original NavigationElement - it no longer
        # has any children.
        url = reverse('kanisa_manage_navigation_delete', args=[first.pk, ])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)

        self.assertEqual([n.pk for n in NavigationElement.objects.all()],
                         [])

        self.client.logout()
