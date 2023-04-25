from datetime import date, timedelta
from django.test import TestCase
from kanisa.models import Banner
from kanisa.utils.banners import date_has_passed, today_in_range
import factory


class BannerFactory(factory.DjangoModelFactory):
    headline = factory.Sequence(lambda n: 'Banner Title #%d' % n)
    contents = 'Banner contents'
    image = 'non_existent_image.jpg'

    class Meta:
        model = Banner


class BannerTest(TestCase):
    def test_is_active(self):
        # A banner with no expiry date or publication date
        banner = BannerFactory.build()
        self.assertTrue(banner.active())

        # A banner which has expired
        banner = BannerFactory.build(publish_until=date(2012, 1, 1))
        self.assertFalse(banner.active())

        # A banner with a long-passed publication date, and a
        # far-future expiration date
        banner = BannerFactory.build(publish_from=date(2012, 1, 1),
                                     publish_until=date(2020, 1, 1))
        self.assertTrue(banner.active())

    def test_has_expired(self):
        # A banner with no expiry date or publication date
        banner = BannerFactory.build()
        self.assertFalse(banner.expired())

        # A banner which has expired
        banner = BannerFactory.build(publish_until=date(2012, 1, 1))
        self.assertTrue(banner.expired())

        # A banner with a long-passed publication date, and a
        # far-future expiration date
        banner = BannerFactory.build(publish_from=date(2012, 1, 1),
                                     publish_until=date(2020, 1, 1))
        self.assertFalse(banner.expired())

    def test_fetch_active(self):
        BannerFactory.create()
        BannerFactory.create(publish_until=date(2012, 1, 1))
        BannerFactory.create(publish_from=date(2020, 1, 1))
        banners = Banner.active_objects.all()
        self.assertEqual(len(banners), 1)

    def test_fetch_inactive(self):
        BannerFactory.create()
        BannerFactory.create(publish_until=date(2012, 1, 1))
        BannerFactory.create(publish_from=date(2020, 1, 1))
        banners = Banner.inactive_objects.all()
        self.assertEqual(len(banners), 2)

    def test_unicode(self):
        banner = BannerFactory.build(headline='Green Flowers')
        self.assertEqual(unicode(banner), 'Green Flowers')

    def test_date_has_passed(self):
        self.assertFalse(date_has_passed(None))
        self.assertTrue(date_has_passed(date(2012, 1, 1)))
        self.assertFalse(date_has_passed(date.today()))

    def test_today_in_range(self):
        self.assertTrue(today_in_range(None, None))
        self.assertTrue(today_in_range(date.today(), None))
        self.assertTrue(today_in_range(None, date.today()))
        self.assertTrue(today_in_range(date.today(), date.today()))
        self.assertTrue(today_in_range(date.today() - timedelta(days=1),
                                       date.today() + timedelta(days=1)))
        self.assertFalse(today_in_range(date.today() - timedelta(days=1),
                                        date.today() - timedelta(days=1)))
        self.assertFalse(today_in_range(date.today() + timedelta(days=1),
                                        date.today() + timedelta(days=1)))
        self.assertFalse(today_in_range(date.today() + timedelta(days=1),
                                        None))
        self.assertFalse(today_in_range(None,
                                        date.today() - timedelta(days=1)))

    def test_set_retired(self):
        # Confirm initial state
        banner = BannerFactory.create()
        self.assertTrue(banner.active())

        # Retire the banner
        banner.set_retired()
        self.assertFalse(banner.active())

        # Test changes were persisted
        banner = Banner.objects.get(pk=banner.pk)
        self.assertFalse(banner.active())

        # Test the inactive banner manager picks it up
        self.assertTrue(banner in Banner.inactive_objects.all())
        self.assertRaises(Banner.DoesNotExist,
                          Banner.active_objects.get, pk=banner.pk)

        # Ensure test doesn't change state
        banner.delete()
