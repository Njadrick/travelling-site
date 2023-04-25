from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.test import TestCase
from kanisa.models import Page
from kanisa.models.pages import get_page_from_path
import factory


class PageFactory(factory.DjangoModelFactory):
    title = 'Page Title'

    class Meta:
        model = Page


class PageTest(TestCase):
    def test_make_non_leaf_node_a_draft(self):
        parent = PageFactory.create()
        PageFactory.create(parent=parent)
        p = Page.objects.get(pk=parent.pk)
        p.draft = True

        with self.assertRaises(ValidationError) as cm:
            p.full_clean()

        errors = cm.exception.message_dict
        self.assertTrue('draft' in errors)
        self.assertEqual(errors['draft'],
                         ['Cannot mark this page as draft, as it has '
                          'published descendants.', ])

    def test_make_leaf_node_a_draft(self):
        leaf = PageFactory.create()
        leaf.draft = True
        leaf.full_clean()

    def test_publish_child_of_draft_node(self):
        parent = PageFactory.create(draft=True)
        child = PageFactory.build(parent=parent, draft=False)

        with self.assertRaises(ValidationError) as cm:
            child.full_clean()

        errors = cm.exception.message_dict
        self.assertTrue('draft' in errors)
        self.assertEqual(errors['draft'],
                         ['Cannot mark this page as published, as its '
                          'parent page (Page Title) is currently a draft.', ])

    def test_page_cannot_be_its_own_parent(self):
        p = PageFactory.create()
        p.parent = p

        with self.assertRaises(ValidationError) as cm:
            p.full_clean()

        errors = cm.exception.message_dict
        self.assertTrue('parent' in errors)
        self.assertEqual(errors['parent'],
                         ['A page cannot be its own parent.', ])

    def test_page_cannot_have_descendant_as_parent(self):
        parent = PageFactory.create()
        child = PageFactory.create(parent=parent)

        parent.parent = child

        with self.assertRaises(ValidationError) as cm:
            parent.full_clean()

        errors = cm.exception.message_dict
        self.assertTrue('parent' in errors)
        self.assertEqual(errors['parent'],
                         ['Invalid parent - cyclical hierarchy '
                          'detected.', ])

    def test_get_path_for_root_node(self):
        page = PageFactory.create(title='hello')

        with self.assertNumQueries(0):
            self.assertEqual('hello/', page.get_path())

    def test_get_path_for_grandchild_node(self):
        root = PageFactory.create(title='hello')
        child = PageFactory.create(title='comma', parent=root)
        grandchild = PageFactory.create(title='world', parent=child)

        with self.assertNumQueries(1):
            self.assertEqual('hello/comma/', child.get_path())

        with self.assertNumQueries(1):
            self.assertEqual('hello/comma/world/', grandchild.get_path())

        # Check we still only do one query even if we reload the
        # object from scratch (just in case fetching the path for the
        # child node cached things in object).
        grandchild = Page.objects.get(pk=grandchild.pk)
        with self.assertNumQueries(1):
            self.assertEqual('hello/comma/world/', grandchild.get_path())


class GetPageFromPathTest(TestCase):
    def test_raises_http_404_on_empty_request(self):
        with self.assertNumQueries(0):
            with self.assertRaises(Page.DoesNotExist):
                get_page_from_path('')

            with self.assertRaises(Page.DoesNotExist):
                get_page_from_path('/')

    def test_root_page(self):
        page = PageFactory.create(title='Hello')
        self.assertEqual(page.slug, 'hello')

        with self.assertNumQueries(1):
            self.assertEqual(page, get_page_from_path('/hello/'))

    def test_root_page_double_slash(self):
        page = PageFactory.create(title='Hello')
        self.assertEqual(page.slug, 'hello')

        with self.assertNumQueries(1):
            with self.assertRaises(Page.DoesNotExist):
                get_page_from_path('/hello//')

    def test_root_page_without_trailing_slash(self):
        page = PageFactory.create(title='Hello')
        self.assertEqual(page.slug, 'hello')

        with self.assertNumQueries(0):
            with self.assertRaises(Page.DoesNotExist):
                get_page_from_path('/hello')

    def test_nonexistent_root_page(self):
        with self.assertNumQueries(1):
            with self.assertRaises(Page.DoesNotExist):
                get_page_from_path('/hello/')

    def test_fetch_unpublished_page_fails(self):
        page = PageFactory.create(title='Hello',
                                  draft=True)
        self.assertEqual(page.slug, 'hello')

        with self.assertNumQueries(1):
            with self.assertRaises(Page.DoesNotExist):
                get_page_from_path('/hello/')

    def test_fetch_child_page_without_path_fails(self):
        root = PageFactory.create(title='root')
        PageFactory.create(title='child', parent=root)

        with self.assertNumQueries(1):
            with self.assertRaises(Page.DoesNotExist):
                get_page_from_path('/child/')

    def test_fetch_child_page(self):
        root = PageFactory.create(title='root')
        child = PageFactory.create(title='child', parent=root)
        child2 = PageFactory.create(title='child2', parent=root)
        grandchild = PageFactory.create(title='grandchild', parent=child)
        PageFactory.create(title='grandchild2', parent=child)
        PageFactory.create(title='grandchild3', parent=child2)

        with self.assertNumQueries(2):
            matched = get_page_from_path('/root/child/grandchild/')
            self.assertEqual(grandchild, matched)

    def test_fetch_child_page_without_trailing_slash(self):
        root = PageFactory.create(title='root')
        child = PageFactory.create(title='child', parent=root)
        child2 = PageFactory.create(title='child2', parent=root)
        PageFactory.create(title='grandchild', parent=child)
        PageFactory.create(title='grandchild2', parent=child)
        PageFactory.create(title='grandchild3', parent=child2)

        with self.assertNumQueries(0):
            with self.assertRaises(Page.DoesNotExist):
                get_page_from_path('/root/child/grandchild')

    def test_fetch_child_page_with_repeated_part(self):
        root = PageFactory.create(title='root')
        child = PageFactory.create(title='child', parent=root)
        child2 = PageFactory.create(title='child2', parent=root)
        PageFactory.create(title='grandchild', parent=child)
        PageFactory.create(title='grandchild2', parent=child)
        PageFactory.create(title='grandchild3', parent=child2)

        with self.assertNumQueries(2):
            with self.assertRaises(Page.DoesNotExist):
                get_page_from_path('/root/root/child/grandchild/')

        with self.assertNumQueries(2):
            with self.assertRaises(Page.DoesNotExist):
                get_page_from_path('/root/child/child/grandchild/')

    def test_fetch_path_with_existent_prefix_fails_on_nonexistent_suffix(self):
        root = PageFactory.create(title='root')
        PageFactory.create(title='child', parent=root)

        with self.assertNumQueries(2):
            with self.assertRaises(Page.DoesNotExist):
                get_page_from_path('/root/child/foobar/')

    def test_fetch_path_with_missing_part_halfway_through(self):
        root = PageFactory.create(title='root')
        child = PageFactory.create(title='child', parent=root)
        PageFactory.create(title='grandchild', parent=child)

        with self.assertNumQueries(2):
            with self.assertRaises(Page.DoesNotExist):
                get_page_from_path('/root/foobar/child/')

    def test_fetch_path_with_wrong_parent(self):
        root = PageFactory.create(title='root')
        child = PageFactory.create(title='child', parent=root)
        PageFactory.create(title='grandchild', parent=child)

        with self.assertNumQueries(2):
            with self.assertRaises(Page.DoesNotExist):
                get_page_from_path('/root/grandchild/')

    def test_fetch_non_root_draft_page(self):
        root = PageFactory.create(title='root')
        PageFactory.create(title='child', parent=root, draft=True)

        with self.assertNumQueries(2):
            with self.assertRaises(Page.DoesNotExist):
                get_page_from_path('/root/child/')

    def test_fetch_child_of_page_with_no_children(self):
        PageFactory.create(title='root')

        with self.assertNumQueries(1):
            with self.assertRaises(Page.DoesNotExist):
                get_page_from_path('/root/child/')


class PageTemplatesTest(TestCase):
    def test_breadcrumbs(self):
        root = PageFactory.create(title='hello')
        child = PageFactory.create(title='comma', parent=root)
        grandchild = PageFactory.create(title='world', parent=child)
        greatgrandchild = PageFactory.create(title='Exclamation Mark',
                                             parent=grandchild)

        with self.assertNumQueries(0):
            result = render_to_string('kanisa/public/pages/_breadcrumbs.html',
                                      {'page': root})

        with self.assertNumQueries(1):
            result = render_to_string('kanisa/public/pages/_breadcrumbs.html',
                                      {'page': child})

        with self.assertNumQueries(1):
            result = render_to_string('kanisa/public/pages/_breadcrumbs.html',
                                      {'page': grandchild})

        with self.assertNumQueries(1):
            result = render_to_string('kanisa/public/pages/_breadcrumbs.html',
                                      {'page': greatgrandchild})

        self.assertTrue('"/hello/"' in result)
        self.assertTrue('"/hello/comma/"' in result)
        self.assertTrue('"/hello/comma/world/"' in result)

    def test_nav(self):
        root = PageFactory.create(title='hello')
        child = PageFactory.create(title='comma', parent=root)
        PageFactory.create(title='Full Stop', parent=root)
        grandchild = PageFactory.create(title='world', parent=child)
        PageFactory.create(title='Exclamation Mark',
                           parent=grandchild)
        PageFactory.create(title='Colon',
                           parent=grandchild)
        PageFactory.create(title='Semicolon',
                           parent=grandchild)

        def _get_context(page):
            parent_path = None
            if page.parent:
                parent_path = page.parent.get_path()

            return {'page': page,
                    'parent': page.parent,
                    'parent_path': parent_path,
                    'siblings': list(page.get_published_siblings()),
                    'children': list(page.get_published_children())}

        with self.assertNumQueries(1):
            context = _get_context(root)

        with self.assertNumQueries(0):
            render_to_string('kanisa/public/pages/_nav.html',
                             context)

        with self.assertNumQueries(2):
            context = _get_context(child)

        with self.assertNumQueries(0):
            render_to_string('kanisa/public/pages/_nav.html',
                             context)

        with self.assertNumQueries(3):
            context = _get_context(grandchild)

        with self.assertNumQueries(0):
            render_to_string('kanisa/public/pages/_nav.html',
                             context)
