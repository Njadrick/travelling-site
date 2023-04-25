from django.contrib.auth import get_user_model
from django.core import mail
from django.core.urlresolvers import reverse
from tests.utils import KanisaViewTestCase


class PasswordResetViewTest(KanisaViewTestCase):
    def setUp(self):
        super(PasswordResetViewTest, self).setUp()
        self.fred = get_user_model().objects.get(username='fred')
        self.fred.set_password('secret')
        self.fred.save()

    def test_password_change_view_requires_login(self):
        resp = self.client.get(reverse('kanisa_members_password_change'))
        self.assertEqual(resp.status_code, 302)

    def test_password_change_view_loads(self):
        self.client.login(username='fred', password='secret')
        resp = self.client.get(reverse('kanisa_members_password_change'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'kanisa/management/password_reset.html')
        self.client.logout()

    def test_password_change_view_success(self):
        self.client.login(username='fred', password='secret')
        resp = self.client.post(reverse('kanisa_members_password_change'),
                                {'old_password': 'secret',
                                 'new_password1': 'abcdef',
                                 'new_password2': 'abcdef'})
        self.assertRedirects(resp, '/members/')
        self.client.logout()

    def test_password_recovery_does_not_require_password(self):
        resp = self.client.get(reverse('kanisa_members_recover_password'))
        self.assertEqual(resp.status_code, 200)

    def test_password_recovery_reset_done_view(self):
        resp = self.client.get(reverse('kanisa_members_reset_password_done'))
        self.assertEqual(resp.status_code, 200)

    def test_password_recovery_by_email(self):
        resp = self.client.post(reverse('kanisa_members_recover_password'),
                                {'username_or_email': 'fred@example.com'},
                                follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'fred@example.com')
        self.assertTemplateUsed(
            resp,
            'kanisa/auth/passwordreset/recovery_mail_sent.html'
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['fred@example.com', ])
        self.assertEqual(mail.outbox[0].subject,
                         'Password recovery on testserver')
        likely_urls = [l for l in mail.outbox[0].body.splitlines()
                       if l.startswith('http://testserver')]
        self.assertEqual(len(likely_urls), 1)
        url = likely_urls[0]

        # Grab the password reset URL, and check it renders
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,
                                'kanisa/auth/passwordreset/reset_form.html')

        # Check we can actually change our password with that URL
        resp = self.client.post(url,
                                {'password1': 'honeyichangedmypassword',
                                 'password2': 'honeyichangedmypassword'},
                                follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,
                                'kanisa/auth/passwordreset/reset_done.html')

        new_fred = get_user_model().objects.get(username='fred')
        self.assertTrue(new_fred.check_password('honeyichangedmypassword'))

    def test_password_recovery_by_username(self):
        # Only test up to the email being sent, everything else is the
        # same.
        resp = self.client.post(reverse('kanisa_members_recover_password'),
                                {'username_or_email': 'fred'},
                                follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'fred@example.com')
        self.assertTemplateUsed(
            resp,
            'kanisa/auth/passwordreset/recovery_mail_sent.html'
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['fred@example.com', ])
        self.assertEqual(mail.outbox[0].subject,
                         'Password recovery on testserver')
        likely_urls = [l for l in mail.outbox[0].body.splitlines()
                       if l.startswith('http://testserver')]
        self.assertEqual(len(likely_urls), 1)

    def test_password_recovery_by_mistake(self):
        resp = self.client.post(reverse('kanisa_members_recover_password'),
                                {'username_or_email': 'fredsdjkhfs'})
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp, 'form', 'username_or_email',
                             'Sorry, this user doesn\'t exist.')
        self.assertEqual(len(mail.outbox), 0)
