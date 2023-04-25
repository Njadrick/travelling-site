from datetime import date, time
from django.core.urlresolvers import reverse
from kanisa.models import (
    EventContact,
    RegularEvent,
    ScheduledEvent,
    ScheduledEventSeries
)
from tests.utils import KanisaViewTestCase
import factory


class RegularEventFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'Regular Event #%d' % n)
    start_time = time(14, 0)
    duration = 60
    pattern = "RRULE:FREQ=WEEKLY;BYDAY=TU"

    class Meta:
        model = RegularEvent


class DiaryManagementViewTest(KanisaViewTestCase):
    def test_views_protected(self):
        prefix = 'kanisa_manage_diary'
        self.view_is_restricted(reverse(prefix))
        self.view_is_restricted(reverse('%s_regularevents'
                                        % prefix))
        self.view_is_restricted(reverse('%s_schedule_weeks_regular_event'
                                        % prefix))

    def test_diary_root_view(self):
        RegularEventFactory.create()

        url = reverse('kanisa_manage_diary')
        self.client.login(username='fred', password='secret')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'kanisa/management/diary/index.html')
        self.assertTrue('calendar' in resp.context)
        self.assertTrue('events_to_schedule' in resp.context)
        self.assertTrue(resp.context['events_to_schedule'])
        self.assertEqual(len(resp.context['calendar']), 7)

    def test_diary_root_view_bad_date(self):
        RegularEventFactory.create()

        url = reverse('kanisa_manage_diary') + '?date=abc'
        self.client.login(username='fred', password='secret')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'kanisa/management/diary/index.html')
        self.assertTrue('calendar' in resp.context)
        self.assertTrue('events_to_schedule' in resp.context)
        self.assertTrue(resp.context['events_to_schedule'])
        self.assertEqual(len(resp.context['calendar']), 7)

    def test_diary_regular_events_view(self):
        RegularEventFactory.create()
        RegularEventFactory.create()

        url = reverse('kanisa_manage_diary_regularevents')
        self.client.login(username='fred', password='secret')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp,
                                'kanisa/management/diary/regular_events.html')
        self.assertTrue('regularevent_list' in resp.context)
        self.assertEqual(len(resp.context['regularevent_list']), 2)

    def test_diary_schedule_regular_event(self):
        pk = RegularEventFactory.create(title='Afternoon Tea').pk
        # Check preconditions
        self.assertEqual(len(ScheduledEvent.objects.all()), 0)

        url = reverse('kanisa_manage_diary_schedule_regular_event',
                      args=[pk, 20120103, ])
        self.client.login(username='fred', password='secret')

        # Schedule the event
        resp = self.client.get(url, follow=True)
        expected_location = reverse('kanisa_manage_diary') + '?date=20120103'
        self.assertRedirects(resp, expected_location)
        self.assertTrue('messages' in resp.context)
        self.assertEqual([m.message for m in resp.context['messages']],
                         ['Afternoon Tea scheduled for 3 Jan 2012 at 2 p.m.',
                          ])

        self.assertEqual(len(ScheduledEvent.objects.all()), 1)

        # shouldn't be able to schedule it again
        resp = self.client.get(url, follow=True)
        self.assertRedirects(resp, expected_location)
        self.assertTrue('messages' in resp.context)
        self.assertEqual([m.message for m in resp.context['messages']],
                         [('Afternoon Tea already scheduled for 3 Jan 2012 at '
                           '2 p.m.'),
                          ])

    def test_diary_schedule_nonexistent_regular_event_404s(self):
        url = reverse('kanisa_manage_diary_schedule_regular_event',
                      args=[30, 20120101, ])
        self.client.login(username='fred', password='secret')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_diary_schedule_regular_event_baddate_404s(self):
        pk = RegularEventFactory.create(title='Afternoon Tea').pk
        url = reverse('kanisa_manage_diary_schedule_regular_event',
                      args=[pk, 20121301, ])
        self.client.login(username='fred', password='secret')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_diary_cancel_scheduled_event(self):
        # Check preconditions
        self.assertEqual(len(ScheduledEvent.objects.all()), 0)

        # Schedule an event
        pk = RegularEventFactory.create(title='Afternoon Tea').pk
        event = RegularEvent.objects.get(pk=pk)
        event.schedule(date(2012, 01, 03), date(2012, 01, 04))
        self.assertEqual(len(ScheduledEvent.objects.all()), 1)

        pk = ScheduledEvent.objects.all()[0].pk

        url = reverse('kanisa_manage_diary_cancel_scheduled_event',
                      args=[pk, ])
        self.client.login(username='fred', password='secret')
        resp = self.client.post(url, follow=True)
        expected_location = reverse('kanisa_manage_diary') + '?date=20120103'
        self.assertRedirects(resp, expected_location)
        self.assertTrue('messages' in resp.context)
        self.assertEqual([m.message for m in resp.context['messages']],
                         ['Afternoon Tea cancelled on 3 Jan 2012 at 2 p.m.',
                          ])

        self.assertEqual(len(ScheduledEvent.objects.all()), 0)

    def test_diary_cancel_scheduled_event_nonexistent_404s(self):
        # Check preconditions
        self.assertEqual(len(ScheduledEvent.objects.all()), 0)

        url = reverse('kanisa_manage_diary_cancel_scheduled_event',
                      args=[40, ])

        self.client.login(username='fred', password='secret')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_diary_schedule_weeks_events(self):
        tuesdays = "RRULE:FREQ=WEEKLY;BYDAY=TU"
        wednesdays = "RRULE:FREQ=WEEKLY;BYDAY=WE"
        thursdays = "RRULE:FREQ=WEEKLY;BYDAY=TH"

        RegularEventFactory.create(pattern=tuesdays)
        RegularEventFactory.create(pattern=wednesdays)
        RegularEventFactory.create(pattern=thursdays)

        # Check preconditions
        self.assertEqual(len(ScheduledEvent.objects.all()), 0)
        url = reverse('kanisa_manage_diary_schedule_weeks_regular_event')

        # Scheduling events should schedule them
        self.client.login(username='fred', password='secret')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('messages' in resp.context)
        self.assertEqual([m.message for m in resp.context['messages']],
                         [('I\'ve scheduled this week\'s events for you - '
                           'enjoy!'), ])

        self.assertEqual(len(ScheduledEvent.objects.all()), 3)

        # Trying again should error out
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('messages' in resp.context)
        self.assertEqual([m.message for m in resp.context['messages']],
                         [('No events to schedule.'), ])
        self.assertEqual(len(ScheduledEvent.objects.all()), 3)

    def test_diary_event_cloning(self):
        someone = EventContact.objects.create(
            name='Bugs Bunny',
            email='bugs@example.com'
        )
        series = ScheduledEventSeries.objects.create(
            name='My Series'
        )
        original = ScheduledEvent.objects.create(
            title='Foobar',
            date=date(2014, 03, 31),
            start_time=time(9, 0),
            duration=60,
            contact=someone,
            intro='Test event',
            details='All my details',
            series=series
        )

        self.client.login(username='fred', password='secret')
        url = reverse('kanisa_manage_diary_clone_scheduled_event')
        resp = self.client.get(url, {'event': original.pk})
        self.assertEqual(resp.status_code, 200)

        self.assertTrue('form' in resp.context)

        # Make sure all the data is copied across
        form_data = resp.context['form'].initial
        self.assertEqual(form_data.get('title', None), 'Foobar')
        self.assertEqual(form_data.get('start_time', None), time(9, 0))
        self.assertEqual(form_data.get('duration', None), 60)
        self.assertEqual(form_data.get('contact', None), someone)
        self.assertEqual(form_data.get('details', None), 'All my details')
        self.assertEqual(form_data.get('intro', None), 'Test event')
        self.assertEqual(form_data.get('series', None), series)

        # Cloned events should have no pre-filled date (that's the
        # point of them).
        self.assertEqual(form_data.get('date', None), None)


class DiaryPublicViewTest(KanisaViewTestCase):
    def test_view_index(self):
        url = reverse('kanisa_public_diary_index')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_view_regular_event(self):
        event = RegularEventFactory.create()
        url = reverse('kanisa_public_diary_regularevent_detail',
                      args=[event.slug, ])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
