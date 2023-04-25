from datetime import date, time, datetime
from django.test import TestCase
from kanisa.models import diary
from kanisa.models import (
    RegularEvent,
    ScheduledEvent,
    ScheduledEventSeries
)
from kanisa.utils.diary import get_week_bounds, get_schedule
import factory


class RegularEventFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'Regular Event #%d' % n)
    start_time = time(14, 0)
    duration = 60
    pattern = ''

    class Meta:
        model = RegularEvent


class DiaryTest(TestCase):
    def test_unicode(self):
        event = RegularEventFactory.build(title='Afternoon Tea')
        self.assertEqual(unicode(event), 'Afternoon Tea')

    def test_schedule(self):
        pattern = "RRULE:FREQ=WEEKLY;BYDAY=TU"
        event = RegularEventFactory.create(pattern=pattern)
        event.schedule(date(2012, 1, 1), date(2012, 1, 8))

        instances = event.scheduledevent_set.all()
        self.assertEqual(len(instances), 1)

        instance = instances[0]
        self.assertEqual(instance.date, date(2012, 1, 3))
        self.assertEqual(instance.start_time, time(14, 0, 0))
        self.assertEqual(instance.duration, 60)

    def test_instance_unicode(self):
        friday = "RRULE:FREQ=WEEKLY;BYDAY=FR"
        event = RegularEventFactory.create(title='Breakfast Club',
                                           pattern=friday)
        event.schedule(date(2012, 1, 1), date(2012, 1, 8))

        instance = ScheduledEvent.objects.get(pk=1)

        with self.assertNumQueries(0):
            self.assertEqual(unicode(instance), 'Breakfast Club')

        instance.title = 'Special Breakfast'
        instance.save()

        instance = ScheduledEvent.objects.get(pk=1)
        with self.assertNumQueries(0):
            self.assertEqual(unicode(instance), 'Special Breakfast')

        instance.title = ''
        instance.save()

        instance = ScheduledEvent.objects.get(pk=1)

        with self.assertNumQueries(0):
            self.assertEqual(unicode(instance), 'Breakfast Club')

    def test_get_next_with_event_scheduled(self):
        tuesdays = "RRULE:FREQ=WEEKLY;BYDAY=TU"
        event = RegularEventFactory.create(
            title='Breakfast Club',
            pattern=tuesdays
        )

        # I should probably mock out datetime.now() here, so I don't
        # have to use such a far-future date.
        event.schedule(date(2020, 1, 1), date(2020, 1, 31))
        next = event.get_next()
        self.assertEqual(next.title, 'Breakfast Club')
        self.assertEqual(next.date, date(2020, 1, 7))

    def test_get_next_without_event_scheduled(self):
        event = RegularEventFactory.create(title='Breakfast Club')
        next = event.get_next()
        self.assertEqual(next, None)

    def test_get_next_with_event_earlier_today(self):
        regular_event = RegularEventFactory.create(title='Breakfast Club')
        ScheduledEvent.objects.create(
            event=regular_event,
            title=regular_event.title,
            date=date.today(),
            start_time=time(8, 59),
            intro='Something interesting'
        )

        next = regular_event.get_next(
            datetime.combine(date.today(), time(9, 0))
        )
        self.assertEqual(next, None)

    def test_get_next_with_event_later_today(self):
        regular_event = RegularEventFactory.create(title='Breakfast Club')
        event = ScheduledEvent.objects.create(
            event=regular_event,
            title=regular_event.title,
            date=date.today(),
            start_time=time(9, 1),
            intro='Something interesting'
        )

        next = regular_event.get_next(
            datetime.combine(date.today(), time(9, 0))
        )
        self.assertEqual(next, event)


class DiaryGetWeekBoundsTest(TestCase):
    def test_get_week_bounds_today(self):
        monday, sunday = get_week_bounds()
        self.assertEqual(monday.weekday(), 0)
        self.assertEqual(sunday.weekday(), 6)
        self.assertTrue(monday <= date.today())
        self.assertTrue(sunday >= date.today())

    def test_get_week_bounds_on_date(self):
        monday, sunday = get_week_bounds(date(2012, 6, 12))
        self.assertEqual(monday.weekday(), 0)
        self.assertEqual(sunday.weekday(), 6)
        self.assertEqual(monday, date(2012, 6, 11))
        self.assertEqual(sunday, date(2012, 6, 17))

    def test_get_week_bounds_on_a_monday(self):
        monday, sunday = get_week_bounds(date(2012, 6, 11))
        self.assertEqual(monday.weekday(), 0)
        self.assertEqual(sunday.weekday(), 6)
        self.assertEqual(monday, date(2012, 6, 11))
        self.assertEqual(sunday, date(2012, 6, 17))

    def test_get_week_bounds_on_a_sunday(self):
        monday, sunday = get_week_bounds(date(2012, 6, 17))
        self.assertEqual(monday.weekday(), 0)
        self.assertEqual(sunday.weekday(), 6)
        self.assertEqual(monday, date(2012, 6, 11))
        self.assertEqual(sunday, date(2012, 6, 17))


class DiaryGetScheduleTest(TestCase):
    def test_basics(self):
        tuesday = "RRULE:FREQ=WEEKLY;BYDAY=TU"
        wednesday = "RRULE:FREQ=WEEKLY;BYDAY=WE"
        thursday = "RRULE:FREQ=WEEKLY;BYDAY=TH"
        friday = "RRULE:FREQ=WEEKLY;BYDAY=FR"
        event1 = RegularEventFactory.create(pattern=tuesday)
        event2 = RegularEventFactory.create(pattern=friday)
        RegularEventFactory.create(pattern=wednesday)
        RegularEventFactory.create(pattern=thursday)
        schedule = get_schedule()
        self.assertTrue(hasattr(schedule, 'calendar_entries'))
        self.assertEqual(len(schedule.calendar_entries), 7)

        entries = schedule.calendar_entries

        days_of_week = [d[1] for d in diary.DAYS_OF_WEEK]
        self.assertEqual(days_of_week,
                         [s.dayname for s in entries])
        self.assertEqual(range(0, 7),
                         [s.day for s in entries])

        self.assertEqual([len(e.regular_events) for e in entries],
                         [0, 1, 1, 1, 1, 0, 0])
        self.assertEqual(entries[1].regular_events[0],
                         event1)
        self.assertEqual(entries[4].regular_events[0],
                         event2)

    def test_scheduled(self):
        tuesday = "RRULE:FREQ=WEEKLY;BYDAY=TU"
        event1 = RegularEventFactory.create(pattern=tuesday)
        RegularEventFactory.create(pattern="RRULE:FREQ=WEEKLY;BYDAY=WE")

        event1.schedule(date(2012, 1, 1),
                        date(2012, 1, 8))
        self.assertEqual(len(ScheduledEvent.objects.all()),
                         1)
        instance = ScheduledEvent.objects.get(pk=1)
        self.assertEqual(instance.date, date(2012, 1, 3))

        schedule = get_schedule(date(2012, 1, 4))
        entries = schedule.calendar_entries

        # Regular events is a weekday aligned list of regular events
        # which are not yet scheduled.
        self.assertEqual([len(e.regular_events) for e in entries],
                         [0, 0, 1, 0, 0, 0, 0])

        # Scheduled events is a weekday aligned list of scheduled
        # events which are scheduled.
        self.assertEqual([len(e.scheduled_events) for e in entries],
                         [0, 1, 0, 0, 0, 0, 0])


class ScheduledEventFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'Event #%d' % n)
    start_time = time(14, 0)
    date = date(2012, 6, 15)

    class Meta:
        model = ScheduledEvent


class DiaryScheduledEventTest(TestCase):
    def test_unicode(self):
        event = ScheduledEventFactory.build(title='Afternoon Tea')
        self.assertEqual(unicode(event), 'Afternoon Tea')

    def test_end_date(self):
        # end_date should be auto-populated
        event1 = ScheduledEventFactory.create()
        self.assertEqual(event1.end_date, date(2012, 6, 15))

    def test_events_between(self):
        event1 = ScheduledEventFactory.create(title='1')
        event2 = ScheduledEventFactory.create(title='2',
                                              date=date(2012, 6, 12))
        event3 = ScheduledEventFactory.create(title='3',
                                              date=date(2012, 6, 19))
        early_event = ScheduledEventFactory.create(title='early',
                                                   date=date(2012, 6, 11))
        late_event = ScheduledEventFactory.create(title='late',
                                                  date=date(2012, 6, 20))

        events = ScheduledEvent.events_between(date(2012, 6, 12),
                                               date(2012, 6, 19))

        self.assertEqual(list(events),
                         [event2, event1, event3, ])

        events = ScheduledEvent.events_between(date(2012, 6, 11),
                                               date(2012, 6, 15))

        self.assertEqual(list(events),
                         [early_event, event2, event1, ])

        events = ScheduledEvent.events_between(date(2012, 6, 12),
                                               date(2012, 6, 20))

        self.assertEqual(list(events),
                         [event2, event1, event3, late_event, ])

    def test_events_between_multi_day_during(self):
        event1 = ScheduledEventFactory.create(end_date=date(2012, 6, 16))
        events = ScheduledEvent.events_between(date(2012, 6, 11),
                                               date(2012, 6, 15))

        self.assertEqual(list(events),
                         [event1, ])

    def test_events_between_multi_days_before(self):
        event1 = ScheduledEventFactory.create(date=date(2012, 6, 10),
                                              end_date=date(2012, 6, 16))
        # This one ends before the range we care about
        ScheduledEventFactory.create(date=date(2012, 6, 9),
                                     end_date=date(2012, 6, 10))

        events = ScheduledEvent.events_between(date(2012, 6, 11),
                                               date(2012, 6, 15))

        self.assertEqual(list(events),
                         [event1, ])

    def test_events_between_multi_day_after(self):
        event1 = ScheduledEventFactory.create(end_date=date(2012, 6, 20))

        # This one starts after the range we care about
        ScheduledEventFactory.create(date=date(2012, 6, 16),
                                     end_date=date(2012, 6, 20))

        events = ScheduledEvent.events_between(date(2012, 6, 11),
                                               date(2012, 6, 15))

        self.assertEqual(list(events),
                         [event1, ])

    def test_event_series(self):
        series_1 = ScheduledEventSeries.objects.create(name='Event 1')
        series_2 = ScheduledEventSeries.objects.create(name='Event 2')
        self.assertEqual(unicode(series_1), 'Event 1')
        self.assertEqual(unicode(series_2), 'Event 2')

        ScheduledEventFactory.create(date=date(2012, 6, 16),
                                     end_date=date(2012, 6, 20),
                                     series=series_1)

        ScheduledEventFactory.create(date=date(2012, 6, 14),
                                     end_date=date(2012, 6, 20),
                                     series=series_1)

        ScheduledEventFactory.create(date=date(2012, 6, 18),
                                     end_date=date(2012, 6, 20),
                                     series=series_1)

        ScheduledEventFactory.create(date=date(2013, 6, 16),
                                     end_date=date(2013, 6, 20),
                                     series=series_2)

        ScheduledEventFactory.create(date=date(2013, 6, 14),
                                     end_date=date(2013, 6, 20),
                                     series=series_2)

        ScheduledEventFactory.create(date=date(2013, 6, 18),
                                     end_date=date(2013, 6, 20),
                                     series=series_2)

        with self.assertNumQueries(2):
            # It takes 2 queries (one each for series_1 and series_2)
            # since we haven't gone through the manager.
            self.assertEqual(series_1.start_date(), date(2012, 6, 14))
            self.assertEqual(series_1.end_date(), date(2012, 6, 18))
            self.assertEqual(series_2.start_date(), date(2013, 6, 14))
            self.assertEqual(series_2.end_date(), date(2013, 6, 18))

        with self.assertNumQueries(2):
            # We do a query for the series, and then queue up a query
            # for the series.
            series = list(ScheduledEventSeries.objects.all())

        with self.assertNumQueries(0):
            # It takes 1 query since we prefetched events through the
            # manager.
            self.assertEqual(series[0].start_date(), date(2012, 6, 14))
            self.assertEqual(series[1].start_date(), date(2013, 6, 14))

        with self.assertNumQueries(0):
            self.assertEqual(series[0].end_date(), date(2012, 6, 18))
            self.assertEqual(series[1].end_date(), date(2013, 6, 18))
