import django
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.auth.context_processors import PermWrapper
from django.core import mail
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from tests.utils import KanisaViewTestCase
from mock import Mock


class UserManagementViewTest(KanisaViewTestCase):
    def setUp(self):
        super(UserManagementViewTest, self).setUp()

        p = Permission.objects.get(codename='manage_users')
        fred = get_user_model().objects.get(username='fred')
        fred.user_permissions.add(p)
        fred.save()

    def test_views_protected(self):
        self.view_is_restricted(reverse('kanisa_manage_users'))
        self.view_is_restricted(reverse('kanisa_manage_users_activate',
                                        args=[1, ]))

    def test_base_view(self):
        self.client.login(username='fred', password='secret')
        resp = self.client.get(reverse('kanisa_manage_users'))
        self.assertEqual(resp.status_code, 200)

        self.assertTrue('user_list' in resp.context)

        bob = get_user_model().objects.get(username='bob')
        fred = get_user_model().objects.get(username='fred')
        superman = get_user_model().objects.get(username='superman')

        self.assertEqual(list(resp.context['user_list']),
                         [bob, fred, superman, ])

        self.client.logout()

    def test_template_complexity(self):
        tmpl = 'kanisa/management/users/_user_list.html'
        users = list(get_user_model().objects.all())
        user = get_user_model().objects.get(username='superman')
        perms = PermWrapper(user)

        with self.assertNumQueries(0):
            render_to_string(tmpl,
                             {'user_list': users,
                              'user': user,
                              'perms': perms})

    def test_user_activate_view_user_already_active(self):
        self.client.login(username='fred', password='secret')

        bob = get_user_model().objects.get(username='bob')
        bob.is_active = True
        bob.save()

        url = reverse('kanisa_manage_users_activate', args=[bob.pk, ])
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)

        bob = get_user_model().objects.get(username='bob')
        self.assertTrue(bob.is_active)
        self.assertContains(resp, 'account is already active.')

        self.assertEqual(len(mail.outbox), 0)

        self.client.logout()

    def test_user_activate_view_on_inactive_user(self):
        self.client.login(username='fred', password='secret')

        bob = get_user_model().objects.get(username='bob')
        bob.is_active = False
        bob.save()

        url = reverse('kanisa_manage_users_activate', args=[bob.pk, ])
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)

        bob = get_user_model().objects.get(username='bob')
        self.assertTrue(bob.is_active)
        self.assertContains(resp, 'account is now activated.')

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, ['bob@example.com', ])
        self.assertEqual(mail.outbox[0].subject,
                         'Your Church Account Activated')

        self.assertEqual(mail.outbox[1].to, ['fred@example.com', ])
        self.assertEqual(mail.outbox[1].subject,
                         'Your Church: bob\'s account activated')

        self.client.logout()

    def test_user_activate_view_non_existent_user(self):
        self.client.login(username='fred', password='secret')
        url = reverse('kanisa_manage_users_activate', args=[1337, ])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)
        self.client.logout()

    def test_user_update_view_non_existent_user(self):
        self.client.login(username='fred', password='secret')
        url = reverse('kanisa_manage_users_update', args=[1337, ])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)
        self.client.logout()

    def test_user_update_view_get(self):
        self.client.login(username='fred', password='secret')

        bob = get_user_model().objects.get(username='bob')

        url = reverse('kanisa_manage_users_update', args=[bob.pk, ])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.client.logout()

    def test_user_update_view_post(self):
        self.client.login(username='fred', password='secret')

        bob = get_user_model().objects.get(username='bob')

        url = reverse('kanisa_manage_users_update', args=[bob.pk, ])

        mock_file = Mock(spec=django.core.files.File)
        mock_file.configure_mock(name='foo.bar')
        mock_file.read.return_value = "Just some data"

        resp = self.client.post(url, {'email': 'bob@example.net',
                                      'first_name': 'Bob',
                                      'last_name': 'Builder',
                                      'image': mock_file},
                                follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('form' not in resp.context)

        self.assertEqual([m.message for m in resp.context['messages']],
                         ['Registered User "Bob" saved.', ])

        bob = get_user_model().objects.get(username='bob')

        # Clean up after our file
        bob.image.delete()

        self.assertEqual(bob.email, 'bob@example.net')

        self.client.logout()
