from django.core.urlresolvers import resolve
from django.test import TestCase
from django.http import HttpRequest
from django.shortcuts import render
from django.template.loader import render_to_string

from lists.views import home_page
from lists.models import Item


class ItemModelTest(TestCase):

    def test_saving_and_retrieving_model(self):
        first_item = Item()
        first_item.text = "The first (ever) list item"
        first_item.save()

        second_item = Item()
        second_item.text = "Item the second"
        second_item.save()

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]
        self.assertEqual(first_saved_item.text, "The first (ever) list item")
        self.assertEqual(second_saved_item.text, "Item the second")


class HomePageTest(TestCase):

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def test_home_page_returns_correct_html(self):
        request = HttpRequest()
        response = home_page(request)
        expected_html = render_to_string('home.html')
        self.assertEqual(response.content.decode(), expected_html)


class ListViewTest(TestCase):

    def test_uses_list_templates(self):
        response = self.client.get('/lists/the-only-list/')
        self.assertTemplateUsed(response, 'list.html')

    def test_displays_all_list_items(self):
        item1 = Item.objects.create(text = "itemy 1")
        item2 = Item.objects.create(text = "itemy 2")

        response = self.client.get('/lists/the-only-list/')

        self.assertContains(response, 'itemy 1')
        self.assertContains(response, 'itemy 2')

class NewListTest(TestCase):
    ## note: urls without a trailing slash are "action" urls that change db
    def test_saving_a_POST_request(self):
        self.client.post('/lists/new', 
                         {"item_text": "A new list item"})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, "A new list item")

    def test_redirects_after_POST(self):
        response = self.client.post('/lists/new',
                         {'item_text': "A new list item"})
        self.assertRedirects(response, '/lists/the-only-list/')

