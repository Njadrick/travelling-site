from datetime import date, timedelta
from kanisa.models import BlogPost
import factory
import pytest


class BlogPostFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'Title #%d' % n)
    teaser_text = 'Teaser contents'
    main_text = 'Main post contents'
    publish_date = date.today() - timedelta(days=1)

    class Meta:
        model = BlogPost


@pytest.mark.django_db
def test_is_published():
    post = BlogPostFactory.build()
    assert post.published()

    post.publish_date = date.today()
    assert post.published()

    post.publish_date = date.today() + timedelta(days=1)
    assert not post.published()


@pytest.mark.django_db
def test_unicode():
    post = BlogPostFactory.build(
        title='This parrot is dead'
    )
    assert unicode(post) == 'This parrot is dead'


@pytest.mark.django_db
def test_comments_enabled():
    post = BlogPostFactory.build(
        title='This parrot is dead'
    )
    assert post.comments_allowed()

    post.enable_comments = False
    assert not post.comments_allowed()

    post.enable_comments = True
    assert post.comments_allowed()

    post.publish_date = date.today() + timedelta(days=1)
    assert not post.comments_allowed()

    post.publish_date = date.today() + timedelta(days=-15)
    assert post.comments_allowed()

    post.publish_date = date.today() + timedelta(days=-31)
    assert not post.comments_allowed()
