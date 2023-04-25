from datetime import date
from django.template.loader import render_to_string
from django.test import TestCase
from kanisa.models import SermonSeries, Sermon, SermonSpeaker
import factory


class SermonSpeakerFactory(factory.DjangoModelFactory):
    forename = factory.Sequence(lambda n: 'John #%d' % n)
    surname = factory.Sequence(lambda n: 'Doe #%d' % n)

    class Meta:
        model = SermonSpeaker


class SermonSeriesFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'Series #%d' % n)

    class Meta:
        model = SermonSeries


class SermonFactory(factory.DjangoModelFactory):
    speaker = factory.SubFactory(SermonSpeakerFactory)
    series = factory.SubFactory(SermonSeriesFactory)
    title = factory.Sequence(lambda n: 'Sermon #%d' % n)
    date = date(2012, 1, 1)

    class Meta:
        model = Sermon


class SermonTest(TestCase):
    def test_unicode(self):
        series = SermonSeriesFactory.build(title='Series Title')
        self.assertEqual(unicode(series), 'Series Title')

        sermon = SermonFactory.build(title='Sermon Title')
        self.assertEqual(unicode(sermon), 'Sermon Title')

    def test_num_sermons(self):
        series1 = SermonSeriesFactory.create()
        series2 = SermonSeriesFactory.create()

        SermonFactory.create(series=series1)
        SermonFactory.create(series=series1)
        SermonFactory.create(series=series1)

        series1 = SermonSeries.objects.get(pk=series1.pk)
        series2 = SermonSeries.objects.get(pk=series2.pk)

        with self.assertNumQueries(0):
            self.assertEqual(series1.num_sermons(), 3)
            self.assertEqual(series2.num_sermons(), 0)

        series = list(SermonSeries.objects.all())
        with self.assertNumQueries(0):
            self.assertEqual([s.num_sermons() for s in series],
                             [3, 0])

    def test_get_sermon_speaker_is_free(self):
        speaker = SermonSpeakerFactory(forename='Bugs',
                                       surname='Bunny')
        sermon = SermonFactory.create(speaker=speaker)
        sermon = Sermon.objects.get(pk=sermon.pk)

        with self.assertNumQueries(0):
            self.assertEqual(unicode(sermon.speaker), 'Bugs Bunny')

    def test_get_sermon_speaker_name(self):
        speaker = SermonSpeakerFactory.build(forename='Bugs',
                                             surname='Bunny')
        self.assertEqual(speaker.name(), 'Bugs Bunny')

    def test_auto_slug_for_sermon_speaker(self):
        speaker = SermonSpeaker.objects.create(forename="Mickey",
                                               surname="Mouse")
        speaker.save()
        self.assertEqual(speaker.slug, 'mickey-mouse')

    def test_fetch_sermons_for_series(self):
        series1 = SermonSeriesFactory.create()
        SermonFactory.create(series=series1,
                             date=date(2012, 4, 29))
        SermonFactory.create(series=series1,
                             date=date(2012, 5, 13))
        SermonFactory.create(series=series1,
                             date=date(2012, 5, 6))

        series1 = SermonSeries.objects.get(pk=1)
        with self.assertNumQueries(1):
            sermons = list(series1.sermons())

        self.assertEqual(len(sermons), 3)

        # Sermons should be returned in date order, oldest first.
        self.assertEqual([s.date for s in sermons],
                         [date(2012, 4, 29),
                          date(2012, 5, 6),
                          date(2012, 5, 13)])

    def test_date_range(self):
        series1 = SermonSeriesFactory.create(passage='Psalms')
        SermonFactory.create(series=series1,
                             date=date(2012, 4, 29))
        SermonFactory.create(series=series1,
                             date=date(2012, 5, 13))

        # Active series have None as the end-point of the date range.
        with self.assertNumQueries(1):
            self.assertEqual(series1.date_range(),
                             (date(2012, 4, 29),
                              None))

        series1.active = False

        with self.assertNumQueries(1):
            self.assertEqual(series1.date_range(),
                             (date(2012, 4, 29),
                              date(2012, 5, 13)))

        # Series 2 has no sermons
        series2 = SermonSeriesFactory.create(passage='John 21')
        self.assertEqual(series2.sermons().count(), 0)

        with self.assertNumQueries(1):
            self.assertEqual(series2.date_range(),
                             None)

    def test_subtitle_template(self):
        def render(series):
            tmpl = 'kanisa/public/sermons/_subtitle.html'
            return render_to_string(tmpl,
                                    {'object': series}).strip()

        series1 = SermonSeriesFactory.create(passage='Psalms')
        SermonFactory.create(series=series1,
                             date=date(2012, 4, 29))
        SermonFactory.create(series=series1,
                             date=date(2012, 5, 13))

        self.assertEqual(render(series1),
                         ('<small>\n(A series on '
                          '<em>Psalms</em>: 29th April 2012 &ndash; '
                          ')\n</small>'))

        series1.active = False
        self.assertEqual(render(series1),
                         ('<small>\n(A series on '
                          '<em>Psalms</em>: 29th April 2012 &ndash; '
                          '13th May 2012)\n</small>'))

        series1.passage = None
        self.assertEqual(render(series1),
                         ('<small>\n(29th April 2012 '
                          '&ndash; 13th May 2012)\n</small>'))

        series1.active = True
        self.assertEqual(render(series1),
                         ('<small>\n(29th April 2012 '
                          '&ndash; )\n</small>'))

        # Series 2 has no sermons
        series2 = SermonSeriesFactory.create(passage='John 21')
        self.assertEqual(render(series2),
                         ('<small>\n(A series on '
                          '<em>John 21</em>)\n</small>'))
