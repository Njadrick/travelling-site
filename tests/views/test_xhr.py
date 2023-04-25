from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import AnonymousUser
from datetime import date, time
from kanisa.models import (
    Band,
    NavigationElement,
    Page,
    RegularEvent,
    ScheduledEvent,
    SermonSeries,
)
from tests.views.utils import XHRBaseTestCase
from kanisa.views.xhr.bible import CheckBiblePassageView
from kanisa.views.xhr.diary import (
    ScheduleRegularEventView,
    DiaryGetSchedule
)
from kanisa.views.xhr.navigation import (
    ListNavigationView,
    MoveNavigationElementUpView,
    MoveNavigationElementDownView
)
from kanisa.views.xhr.pages import CreatePageView, ListPagesView
from kanisa.views.xhr.sermons import MarkSermonSeriesCompleteView
from kanisa.views.xhr.services import BandInformationView, EventsView
import factory
import json


class XHRBiblePassageViewTest(XHRBaseTestCase):
    url = reverse_lazy('kanisa_xhr_biblepassage_check')
    method = 'post'
    view = CheckBiblePassageView

    def test_must_provide_passage(self):
        request = self.get_request()
        request.user = self.fred
        resp = self.fetch_from_factory(request, {'foo': 'bar'})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content,
                         "Required argument 'passage' not found.")

    def test_invalid_passage(self):
        request = self.get_request()
        request.user = self.fred
        resp = self.fetch_from_factory(request,
                                       {'passage': 'Foobar'})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content,
                         '"Foobar" is not a valid Bible passage.')

    def test_valid_book_invalid_range(self):
        request = self.get_request()
        request.user = self.fred
        resp = self.fetch_from_factory(request,
                                       {'passage': 'Ps 151'})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content,
                         'There are only 150 chapters in Psalms.')

    def test_valid_passage(self):
        request = self.get_request()
        request.user = self.fred
        resp = self.fetch_from_factory(request,
                                       {'passage': 'Matt 3v1-7'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, 'Matthew 3:1-7')


class PageFactory(factory.DjangoModelFactory):
    title = 'Page Title'

    class Meta:
        model = Page


class XHRCreatePageViewTest(XHRBaseTestCase):
    url = reverse_lazy('kanisa_manage_xhr_create_page')
    method = 'post'
    permission_text = 'manage pages'
    view = CreatePageView

    def test_must_provide_required_inputs(self):
        request = self.get_request()
        request.user = self.fred

        # No title
        resp = self.fetch_from_factory(request, {'parent': '3', })
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content,
                         "Required argument 'title' not found.")

        # No parent
        resp = self.fetch_from_factory(request,
                                       {'title': 'Test page', })
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content,
                         "Required argument 'parent' not found.")

    def test_empty_title(self):
        request = self.get_request()
        request.user = self.fred

        # Empty title
        resp = self.fetch_from_factory(request,
                                       {'title': '', 'parent': ''})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content, 'Title must not be empty.')

    def test_nonexistent_parent(self):
        request = self.get_request()
        request.user = self.fred

        resp = self.fetch_from_factory(request,
                                       {'title': 'Test page', 'parent': '99'})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content, 'Page with ID \'99\' not found.')

    def test_empty_parent(self):
        request = self.get_request()
        request.user = self.fred

        resp = self.fetch_from_factory(request,
                                       {'title': 'Test page', 'parent': ''})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, 'Page created.')

    def test_good_parent(self):
        request = self.get_request()
        request.user = self.fred

        pk = PageFactory.create().pk

        resp = self.fetch_from_factory(request,
                                       {'title': 'Test page',
                                        'parent': '%s' % pk})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, 'Page created.')


class XHRListPagesViewTest(XHRBaseTestCase):
    url = reverse_lazy('kanisa_manage_xhr_list_pages')
    method = 'get'
    permission_text = 'manage pages'
    view = ListPagesView

    def test_success(self):
        request = self.get_request()
        request.user = self.fred

        # Make some sample data
        parent = PageFactory.create()
        PageFactory.create(parent=parent)
        PageFactory.create()

        resp = self.fetch_from_factory(request)
        self.assertEqual(resp.status_code, 200)


class SermonSeriesFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'Series #%d' % n)

    class Meta:
        model = SermonSeries


class XHRMarkSermonSeriesComplete(XHRBaseTestCase):
    url = reverse_lazy('kanisa_manage_xhr_sermon_series_complete')
    method = 'post'
    permission_text = 'manage sermons'
    view = MarkSermonSeriesCompleteView

    def test_fails_without_required_parameters(self):
        request = self.get_request()
        request.user = self.fred

        resp = self.fetch_from_factory(request)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content,
                         "Required argument 'series' not found.")

    def test_fails_with_non_numeric_series(self):
        request = self.get_request()
        request.user = self.fred

        resp = self.fetch_from_factory(request,
                                       {'series': 'nonnumeric'})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content,
                         "No sermon series found with ID 'nonnumeric'.")

    def test_fails_with_non_existent_series(self):
        request = self.get_request()
        request.user = self.fred

        resp = self.fetch_from_factory(request, {'series': 99})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content, "No sermon series found with ID '99'.")

    def test_success(self):
        request = self.get_request()
        request.user = self.fred

        pk = SermonSeriesFactory.create().pk

        resp = self.fetch_from_factory(request, {'series': pk})
        self.assertEqual(resp.status_code, 200)


class RegularEventFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'Regular Event #%d' % n)
    start_time = time(14, 0)
    duration = 60
    pattern = "RRULE:FREQ=WEEKLY;BYDAY=TU"

    class Meta:
        model = RegularEvent


class XHRScheduleRegularEventViewTest(XHRBaseTestCase):
    url = reverse_lazy('kanisa_manage_xhr_diary_schedule_regular')
    method = 'post'
    permission_text = 'manage the diary'
    view = ScheduleRegularEventView

    def test_required_attributes_are_required(self):
        request = self.get_request()
        request.user = self.fred

        resp = self.fetch_from_factory(request, {'date': 'foobar'})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content,
                         "Required argument 'event' not found.")

        resp = self.fetch_from_factory(request, {'event': 'foobar'})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content,
                         "Required argument 'date' not found.")

    def test_bad_date_format(self):
        request = self.get_request()
        request.user = self.fred

        resp = self.fetch_from_factory(request,
                                       {'event': 'foobar',
                                        'date': '20121301'})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content, "'20121301' is not a valid date.")

    def test_bad_event_id(self):
        request = self.get_request()
        request.user = self.fred

        resp = self.fetch_from_factory(request,
                                       {'event': '99',
                                        'date': '20121201'})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content, "No event found with ID '99'.")

    def test_success(self):
        request = self.get_request()
        request.user = self.fred

        pk = RegularEventFactory.create().pk
        resp = self.fetch_from_factory(request,
                                       {'event': '%s' % pk,
                                        'date': '20120103'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, "Event scheduled.")

        events = ScheduledEvent.objects.filter(event__pk=1,
                                               date='2012-01-03')
        self.assertEqual(len(events), 1)

    def test_double_schedule(self):
        request = self.get_request()
        request.user = self.fred

        pk = RegularEventFactory.create().pk
        resp = self.fetch_from_factory(request,
                                       {'event': '%s' % pk,
                                        'date': '20120110'})
        self.assertEqual(resp.status_code, 200)

        resp = self.fetch_from_factory(request,
                                       {'event': '%s' % pk,
                                        'date': '20120110'})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content, 'That event is already scheduled.')


class XHRFetchScheduleViewTest(XHRBaseTestCase):
    url = reverse_lazy('kanisa_manage_xhr_diary_get_schedule',
                       args=['20120101', ])
    method = 'get'
    permission_text = 'manage the diary'
    view = DiaryGetSchedule

    def test_success(self):
        request = self.get_request()
        request.user = self.fred

        resp = self.fetch_from_factory(request, date='20120101')
        self.assertEqual(resp.status_code, 200)

    def test_baddate(self):
        request = self.get_request()
        request.user = self.fred

        resp = self.fetch_from_factory(request, date='2012')
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content, "Invalid date '2012' provided.")


class NavigationElementFactory(factory.DjangoModelFactory):
    title = 'Navigation Title'

    class Meta:
        model = NavigationElement


class XHRListNavigationViewTest(XHRBaseTestCase):
    url = reverse_lazy('kanisa_manage_xhr_list_navigation')
    method = 'get'
    permission_text = 'manage navigation'
    view = ListNavigationView

    def test_success(self):
        request = self.get_request()
        request.user = self.fred

        # Make some sample data
        parent = NavigationElementFactory.create()
        NavigationElementFactory.create(parent=parent)
        NavigationElementFactory.create()

        resp = self.fetch_from_factory(request)
        self.assertEqual(resp.status_code, 200)
        tmpl = 'kanisa/management/navigation/_item_list.html'
        self.assertTemplateUsed(tmpl)


class XHRMoveNavigationUpViewTest(XHRBaseTestCase):
    url = reverse_lazy('kanisa_manage_xhr_navigation_up')
    method = 'post'
    permission_text = 'manage navigation'
    view = MoveNavigationElementUpView

    def test_required_arguments(self):
        request = self.get_request()
        request.user = self.fred

        resp = self.fetch_from_factory(request)
        self.assertEqual(resp.content,
                         "Required argument 'navigation_element' not found.")
        self.assertEqual(resp.status_code, 400)

        resp = self.fetch_from_factory(request,
                                       {'navigation_element': "foobar"})
        self.assertEqual(resp.content,
                         "No navigation element found with ID 'foobar'.")
        self.assertEqual(resp.status_code, 400)

        resp = self.fetch_from_factory(request,
                                       {'navigation_element': 3})
        self.assertEqual(resp.content,
                         "No navigation element found with ID '3'.")
        self.assertEqual(resp.status_code, 400)

    def test_move_topmost_element(self):
        first = NavigationElementFactory.create(title='ABC')

        request = self.get_request()
        request.user = self.fred

        resp = self.fetch_from_factory(request,
                                       {'navigation_element': first.pk})
        self.assertEqual(resp.content,
                         "Cannot move element.")
        self.assertEqual(resp.status_code, 400)

    def test_success(self):
        first = NavigationElementFactory.create(title='ABC')
        second = NavigationElementFactory.create(title='XYZ')

        request = self.get_request()
        request.user = self.fred

        self.assertEqual([n.pk for n in NavigationElement.objects.all()],
                         [first.pk, second.pk, ])

        resp = self.fetch_from_factory(request,
                                       {'navigation_element': second.pk})
        self.assertEqual(resp.content,
                         "Element moved.")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual([n.pk for n in NavigationElement.objects.all()],
                         [second.pk, first.pk, ])


class XHRMoveNavigationDownViewTest(XHRBaseTestCase):
    url = reverse_lazy('kanisa_manage_xhr_navigation_down')
    method = 'post'
    permission_text = 'manage navigation'
    view = MoveNavigationElementDownView

    def test_success(self):
        first = NavigationElementFactory.create(title='ABC')
        second = NavigationElementFactory.create(title='XYZ')

        request = self.get_request()
        request.user = self.fred

        self.assertEqual([n.pk for n in NavigationElement.objects.all()],
                         [first.pk, second.pk, ])

        resp = self.fetch_from_factory(request,
                                       {'navigation_element': first.pk})
        self.assertEqual(resp.content,
                         "Element moved.")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual([n.pk for n in NavigationElement.objects.all()],
                         [second.pk, first.pk, ])


class XHRBandInformationViewTestCase(XHRBaseTestCase):
    url = reverse_lazy('kanisa_xhr_bandinformation')
    method = 'get'
    view = BandInformationView

    def test_non_member_access(self):
        request = self.get_request()
        request.user = AnonymousUser()
        resp = self.fetch_from_factory(request)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.content,
                         'You do not have permission to view this page.')

    def test_bad_band(self):
        request = self.get_request()
        request.user = self.fred

        resp = self.fetch_from_factory(request,
                                       {'band_id': 400})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content, 'Invalid band_id')

    def test_good_band(self):
        request = self.get_request()
        request.user = self.fred

        band = Band.objects.create(band_leader=self.fred)

        resp = self.fetch_from_factory(request,
                                       {'band_id': band.pk})
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(data['band_leader'], self.fred.pk)
        self.assertEqual(data['musicians'], [])


class XHREventInformationViewTestCase(XHRBaseTestCase):
    url = reverse_lazy('kanisa_xhr_eventinformation')
    method = 'get'
    view = EventsView

    def test_non_member_access(self):
        request = self.get_request()
        request.user = AnonymousUser()
        resp = self.fetch_from_factory(request)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.content,
                         'You do not have permission to view this page.')

    def test_bad_date(self):
        request = self.get_request()
        request.user = self.fred

        resp = self.fetch_from_factory(request,
                                       {'date': '2013/12/31'})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content, 'Invalid date - should be dd/mm/yyyy')

    def test_good_date_no_events(self):
        request = self.get_request()
        request.user = self.fred

        resp = self.fetch_from_factory(request,
                                       {'date': '31/01/2013'})
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(data['events'], [])

    def test_good_date_with_events(self):
        request = self.get_request()
        request.user = self.fred

        event = ScheduledEvent.objects.create(
            title='Foobar',
            date=date(2013, 1, 31),
            duration=30,
            start_time=time(10, 0)
        )

        resp = self.fetch_from_factory(request,
                                       {'date': '31/01/2013'})
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(data['events'], [[event.pk, event.title], ])
