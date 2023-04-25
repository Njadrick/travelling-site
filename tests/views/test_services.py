import datetime
from django.core.urlresolvers import reverse
from kanisa.models import (
    RegisteredUser,
    ScheduledEvent,
    Service,
)
from tests.utils import KanisaViewTestCase
import factory


class ScheduledEventFactory(factory.DjangoModelFactory):
    title = 'Test Event'
    date = datetime.date(2013, 1, 1)
    start_time = datetime.time(10, 0, 0)
    intro = 'An event for testing with'

    class Meta:
        model = ScheduledEvent


class RegisteredUserFactory(factory.DjangoModelFactory):
    username = 'phil'
    first_name = 'Phil'
    last_name = 'Smith'
    email = 'phil@example.com'

    class Meta:
        model = RegisteredUser


class ServiceFactory(factory.DjangoModelFactory):
    event = factory.SubFactory(ScheduledEventFactory)
    band_leader = factory.SubFactory(RegisteredUserFactory)

    class Meta:
        model = Service


class ServiceMembersViewTest(KanisaViewTestCase):
    def test_views_protected(self):
        self.view_is_restricted(reverse('kanisa_members_services_index'))
        self.view_is_restricted(reverse('kanisa_members_services_index_all'))

    def test_index_view(self):
        # These tests are fairly basic - just testing whether or not
        # the view returns a successful status and uses the templates
        # we expect.
        self.client.login(username='fred', password='secret')

        url = reverse('kanisa_members_services_index')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'kanisa/members/services/index.html')

        url = reverse('kanisa_members_services_index_all')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'kanisa/members/services/index.html')

        self.client.logout()

    def test_detail_view(self):
        self.client.login(username='fred', password='secret')
        service = ServiceFactory.create()

        url = reverse('kanisa_members_services_detail', args=[service.pk, ])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,
                                'kanisa/members/services/service_detail.html')

        self.client.logout()
