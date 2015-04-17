from django.core.urlresolvers import resolve
from django.test import TestCase
from django.http import HttpRequest
from django.shortcuts import render
from django.template.loader import render_to_string

from lists.models import Item, List
from lists.views import home_page

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
        list_ = List.objects.create()
        response = self.client.get('/lists/%d/' % list_.id)
        self.assertTemplateUsed(response, 'list.html')

    def test_displays_items_only_for_that_list(self):
        list_1 = List.objects.create()
        Item.objects.create(text = "itemy 1", list = list_1)
        Item.objects.create(text = "itemy 2", list = list_1)

        list_2 = List.objects.create()
        Item.objects.create(text = "other list item 1", list = list_2)
        Item.objects.create(text = "other list item 2", list = list_2)

        response = self.client.get('/lists/%d/' % list_1.id)

        self.assertContains(response, 'itemy 1')
        self.assertContains(response, 'itemy 2')
        self.assertNotIn(response.content.decode(), 'other list item 1')
        self.assertNotIn(response.content.decode(), 'other list item 2')

    def test_passes_correct_list_to_template(self):
        list_1 = List.objects.create()
        list_2 = List.objects.create()
        response = self.client.get('/lists/%d/' % (list_2.id, ))
        self.assertEqual(response.context['list'], list_2)

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
        list_ = List.objects.first()
        self.assertRegex(response['location'], r'/lists/\d+/')


class NewItemTest(TestCase):

    def test_can_save_POST_request_to_existing_list(self):
        other = List.objects.create()
        correct = List.objects.create()
        response = self.client.post('/lists/%d/add_item' % (correct.id,),
                   data = {"item_text": "new item for existing list"})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, "new item for existing list")
        self.assertEqual(new_item.list, correct)

    def test_redirects_to_correct_list(self):
        other = List.objects.create()
        correct = List.objects.create()
        response = self.client.post('/lists/%d/add_item' % correct.id, 
                    data = {"item_text": "new item for existing list"})
        return self.assertRedirects(response, "/lists/%d/" % (correct.id, ))