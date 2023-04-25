from datetime import date
from django.core.urlresolvers import reverse
from kanisa.models import Banner
from tests.utils import KanisaViewTestCase
from django.test import TestCase
import factory


class BannerFactory(factory.DjangoModelFactory):
    headline = factory.Sequence(lambda n: 'Banner Title #%d' % n)
    contents = 'Banner contents'
    image = 'non_existent_image.jpg'

    class Meta:
        model = Banner


class BannerManagementViewTest(KanisaViewTestCase):
    def test_views_protected(self):
        self.view_is_restricted(reverse('kanisa_manage_banners'))
        self.view_is_restricted(reverse('kanisa_manage_banners_retire',
                                        args=[1, ]))
        self.view_is_restricted(reverse('kanisa_manage_banners_create'))
        self.view_is_restricted(reverse('kanisa_manage_banners_update',
                                        args=[1, ]))

    def test_banner_management_view(self):
        BannerFactory.create()
        BannerFactory.create(publish_until=date(2012, 1, 1))
        BannerFactory.create(publish_from=date(2020, 1, 1))

        url = reverse('kanisa_manage_banners')
        self.client.login(username='fred', password='secret')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'kanisa/management/banners/index.html')

        self.assertTrue('banner_list' in resp.context)
        self.assertEqual([banner.pk for banner in resp.context['banner_list']],
                         [1, ])

    def test_banner_retire_view(self):
        BannerFactory.create(headline="Green Flowers")

        url = reverse('kanisa_manage_banners_retire', args=[1, ])
        self.client.login(username='fred', password='secret')

        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)

        self.assertTrue('banner_list' in resp.context)
        self.assertEqual([banner.pk for banner in resp.context['banner_list']],
                         [])

        self.assertTrue('messages' in resp.context)
        self.assertEqual([m.message for m in resp.context['messages']],
                         [u'Banner "Green Flowers" retired.', ])

    def test_banner_create_view_required_fields(self):
        url = reverse('kanisa_manage_banners_create')
        self.client.login(username='fred', password='secret')
        resp = self.client.post(url, {})
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp, 'form', 'headline',
                             'This field is required.')
        self.assertFormError(resp, 'form', 'image',
                             'This field is required.')


class BannerPublicViewTest(TestCase):
    def test_banner_visit_counting(self):
        banner = BannerFactory.create(url="http://www.google.com")

        url = reverse('kanisa_public_banners_visit', args=[banner.pk, ])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        items = resp.items()

        self.assertEqual(
            [(key, value) for (key, value) in items if key == 'Location'],
            [('Location', 'http://www.google.com')]
        )

        banner = Banner.objects.get(pk=banner.pk)
        self.assertEqual(banner.visits, 1)

    def test_banner_visit_counting_404s_without_url(self):
        banner = BannerFactory.create(url="")
        self.assertEqual(banner.url, '')
        url = reverse('kanisa_public_banners_visit', args=[banner.pk, ])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)
