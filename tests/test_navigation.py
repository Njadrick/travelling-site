from django.core.exceptions import ValidationError
from django.test import TestCase
from kanisa.models import NavigationElement, Page
import factory


class NavigationFactory(factory.DjangoModelFactory):
    title = 'Title'

    class Meta:
        model = NavigationElement


class PageFactory(factory.DjangoModelFactory):
    title = 'Page Title'

    class Meta:
        model = Page


class NavigationElementTest(TestCase):
    def test_unicode(self):
        n = NavigationFactory.build()
        self.assertEqual(unicode(n), 'Title')

    def test_navigation_element_cannot_be_its_own_parent(self):
        n = NavigationFactory.create()
        n.parent = n

        with self.assertRaises(ValidationError) as cm:
            n.full_clean()

        errors = cm.exception.message_dict
        self.assertTrue('parent' in errors)
        self.assertEqual(errors['parent'],
                         ['A navigation element cannot be its own parent.', ])

    def test_navigation_element_cannot_have_child_as_parent(self):
        parent = NavigationFactory.create()
        child = NavigationFactory.create(parent=parent)

        parent.parent = child

        with self.assertRaises(ValidationError) as cm:
            parent.full_clean()

        errors = cm.exception.message_dict
        self.assertTrue('parent' in errors)
        self.assertEqual(errors['parent'],
                         ['Invalid parent - cyclical hierarchy '
                          'detected.', ])

    def test_navigation_element_cannot_have_more_than_two_levels(self):
        parent = NavigationFactory.create()
        child = NavigationFactory.create(parent=parent)
        grandchild = NavigationFactory.create(parent=child)

        with self.assertRaises(ValidationError) as cm:
            grandchild.full_clean()

        errors = cm.exception.message_dict
        self.assertTrue('parent' in errors)
        self.assertEqual(errors['parent'],
                         ['Navigation elements cannot be nested more than 2 '
                          'levels deep.', ])

    def test_move_down_sole_element(self):
        element = NavigationFactory.create()

        with self.assertRaises(NavigationElement.DoesNotExist):
            element.move_down()

    def test_move_down_non_sole_element(self):
        element = NavigationFactory.create()
        sibling = NavigationFactory.create(title="ZTitle")

        element.move_down()

        pks = [n.pk for n in NavigationElement.objects.all()]

        self.assertEqual(pks, [sibling.pk, element.pk])

        element = NavigationElement.objects.get(pk=element.pk)
        sibling = NavigationElement.objects.get(pk=sibling.pk)

        sibling.move_down()

        pks = [n.pk for n in NavigationElement.objects.all()]

        self.assertEqual(pks, [element.pk, sibling.pk])

        element = NavigationElement.objects.get(pk=element.pk)
        sibling = NavigationElement.objects.get(pk=sibling.pk)

        with self.assertRaises(NavigationElement.DoesNotExist):
            sibling.move_down()

    def test_move_up_sole_element(self):
        element = NavigationFactory.create()

        with self.assertRaises(NavigationElement.DoesNotExist):
            element.move_up()

    def test_move_up_non_sole_element(self):
        element = NavigationFactory.create()
        sibling = NavigationFactory.create(title="ZTitle")

        sibling.move_up()

        pks = [n.pk for n in NavigationElement.objects.all()]

        self.assertEqual(pks, [sibling.pk, element.pk])

        element = NavigationElement.objects.get(pk=element.pk)
        sibling = NavigationElement.objects.get(pk=sibling.pk)

        element.move_up()

        pks = [n.pk for n in NavigationElement.objects.all()]

        self.assertEqual(pks, [element.pk, sibling.pk])

        element = NavigationElement.objects.get(pk=element.pk)
        sibling = NavigationElement.objects.get(pk=sibling.pk)

        with self.assertRaises(NavigationElement.DoesNotExist):
            element.move_up()

    def test_add_top_level_navigation_element_for_page(self):
        root_page = PageFactory.create()
        child_page_1 = PageFactory.create(parent=root_page,
                                          title='ABC')
        child_page_2 = PageFactory.create(parent=root_page,
                                          title='XYZ')
        PageFactory.create(parent=root_page, draft=True)
        PageFactory.create(parent=child_page_1)

        url = '/' + root_page.get_path()
        root_navigation = NavigationFactory.create(url=url)

        children = NavigationElement.objects.filter(parent=root_navigation)
        self.assertEqual(len(children), 2)
        self.assertEqual(children[0].url,
                         '/' + child_page_1.get_path())
        self.assertEqual(children[1].url,
                         '/' + child_page_2.get_path())

    def test_add_second_level_navigation_element_for_page(self):
        root_page = PageFactory.create()
        PageFactory.create(parent=root_page,
                           title='ABC')

        root_navigation = NavigationFactory.create(url='/foo/')
        url = '/' + root_page.get_path()
        second_navigation = NavigationFactory.create(url=url,
                                                     parent=root_navigation)

        children = NavigationElement.objects.filter(parent=second_navigation)
        self.assertEqual(len(children), 0)

    def test_add_top_level_navigation_element_for_leaf_page(self):
        root_page = PageFactory.create(draft=True)

        url = '/' + root_page.get_path()
        root_navigation = NavigationFactory.create(url=url)

        children = NavigationElement.objects.filter(parent=root_navigation)
        self.assertEqual(len(children), 0)

    def test_add_page_as_child_of_top_level_navigation_element(self):
        root_page = PageFactory.create()
        url = '/' + root_page.get_path()

        root_navigation = NavigationFactory.create(url=url)

        children = NavigationElement.objects.filter(parent=root_navigation)
        self.assertEqual(len(children), 0)

        PageFactory.create(parent=root_page)
        children = NavigationElement.objects.filter(parent=root_navigation)
        self.assertEqual(len(children), 1)

    def test_add_draft_page_as_child_of_top_level_navigation_element(self):
        root_page = PageFactory.create()
        url = '/' + root_page.get_path()

        root_navigation = NavigationFactory.create(url=url)

        PageFactory.create(parent=root_page, draft=True)
        children = NavigationElement.objects.filter(parent=root_navigation)
        self.assertEqual(len(children), 0)

    def test_edit_page_which_is_child_of_top_level_navigation_element(self):
        root_page = PageFactory.create()
        child_page = PageFactory.create(parent=root_page)
        url = '/' + root_page.get_path()

        root_navigation = NavigationFactory.create(url=url)

        children = NavigationElement.objects.filter(parent=root_navigation)
        self.assertEqual(len(children), 1)
        children.delete()

        child_page.title = 'Foobar'
        child_page.save()

        children = NavigationElement.objects.filter(parent=root_navigation)
        self.assertEqual(len(children), 0)
