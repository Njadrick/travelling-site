from datetime import date
from django.core.urlresolvers import reverse
from kanisa.models import Sermon, SermonSeries, SermonSpeaker
from tests.utils import KanisaViewTestCase
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
    series = factory.SubFactory(SermonSeriesFactory)
    speaker = factory.SubFactory(SermonSpeakerFactory)
    title = factory.Sequence(lambda n: 'Sermon #%d' % n)
    date = date(2012, 1, 1)

    class Meta:
        model = Sermon


class SermonManagementViewTest(KanisaViewTestCase):
    def test_views_protected(self):
        prefix = 'kanisa_manage_sermons'
        self.view_is_restricted(reverse(prefix))
        self.view_is_restricted(reverse('%s_series_create' % prefix))
        self.view_is_restricted(reverse('%s_individual_create' % prefix))
        self.view_is_restricted(reverse('%s_speaker' % prefix))
        self.view_is_restricted(reverse('%s_speaker_create' % prefix))

        self.view_is_restricted(reverse('%s_series_detail' % prefix,
                                        args=[1, ]))
        self.view_is_restricted(reverse('%s_series_update' % prefix,
                                        args=[1, ]))
        self.view_is_restricted(reverse('%s_series_complete' % prefix,
                                        args=[1, ]))
        self.view_is_restricted(reverse('%s_individual_update' % prefix,
                                        args=[1, ]))
        self.view_is_restricted(reverse('%s_speaker_update' % prefix,
                                        args=[1, ]))

    def test_index_view(self):
        SermonSeriesFactory.create()
        SermonSeriesFactory.create()
        SermonFactory.create(series=None)

        self.client.login(username='fred', password='secret')
        resp = self.client.get(reverse('kanisa_manage_sermons'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'kanisa/management/sermons/index.html')

        self.assertEqual(len(resp.context['object_list']), 2)
        self.client.logout()

    def test_create_series_view(self):
        self.client.login(username='fred', password='secret')

        resp = self.client.get(reverse('kanisa_manage_sermons_series_create'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'kanisa/management/create.html')

        self.client.logout()

    def test_create_sermon_view(self):
        pk = SermonSeriesFactory.create(passage='John 21').pk
        self.client.login(username='fred', password='secret')
        base_url = reverse('kanisa_manage_sermons_individual_create')

        # Check with a pre-populated series
        url = '%s?series=%s' % (base_url, pk)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'kanisa/management/create.html')
        self.assertEqual(resp.context['form'].initial['series'], pk)
        self.assertEqual(unicode(resp.context['form'].initial['passage']),
                         'John 21')

        # Check without a pre-populated series
        resp = self.client.get(base_url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'kanisa/management/create.html')
        self.assertTrue('series' not in resp.context['form'].initial)

        # Check with an invalid pre-populated series (series is not an
        # integer)
        url = '%s?series=foobar' % base_url
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

        # Check with an invalid pre-populated series (series does not
        # exist)
        url = '%s?series=42' % base_url
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

        self.client.logout()

    def test_create_speaker_view(self):
        self.client.login(username='fred', password='secret')

        resp = self.client.get(reverse('kanisa_manage_sermons_speaker_create'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'kanisa/management/create.html')

        self.client.logout()

    def test_mark_series_complete(self):
        pk = SermonSeriesFactory.create(title="The Psalms",
                                        active=True).pk

        self.client.login(username='fred', password='secret')

        self.assertTrue(SermonSeries.objects.get(pk=1).active)

        resp = self.client.get(reverse('kanisa_manage_sermons_series_complete',
                                       args=[pk, ]),
                               follow=True)
        self.assertEqual(resp.status_code, 200)

        # Check the relevant message is set
        messages = resp.context['messages']
        self.assertTrue(messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual('Series "The Psalms" marked as complete.',
                         list(messages)[0].message)

        self.assertFalse(SermonSeries.objects.get(pk=pk).active)

        self.client.logout()


class SermonPublicViewTest(KanisaViewTestCase):
    def test_view_sermon_index(self):
        resp = self.client.get(reverse('kanisa_public_sermon_index'))
        self.assertEqual(resp.status_code, 200)

    def test_view_sermon_series(self):
        series = SermonSeriesFactory.create()
        resp = self.client.get(reverse('kanisa_public_sermon_series_detail',
                                       args=[series.slug, ]))
        self.assertEqual(resp.status_code, 200)

    def test_view_sermon_which_is_part_of_a_series(self):
        series = SermonSeriesFactory.create()
        sermon = SermonFactory.create(series=series)

        resp = self.client.get(reverse('kanisa_public_sermon_detail',
                                       args=[sermon.series.slug,
                                             sermon.slug, ]))
        self.assertEqual(resp.status_code, 200)

    def test_view_sermon_which_is_not_part_of_a_series(self):
        sermon = SermonFactory.create(series=None)
        url = reverse('kanisa_public_standalone_sermon_detail',
                      args=[sermon.slug, ])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_standalone_view_404s_for_sermons_in_a_series(self):
        series = SermonSeriesFactory.create()
        sermon = SermonFactory.create(series=series)
        self.assertNotEqual(sermon.series, None)

        url = reverse('kanisa_public_standalone_sermon_detail',
                      args=[sermon.slug, ])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_must_provide_correct_series_to_view_sermon(self):
        series = SermonSeriesFactory.create()
        sermon = SermonFactory.create(series=series)

        resp = self.client.get(reverse('kanisa_public_sermon_detail',
                                       args=['foobar',
                                             sermon.slug, ]))
        self.assertEqual(resp.status_code, 404)
