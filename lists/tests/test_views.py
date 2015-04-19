from django.core.urlresolvers import resolve
from django.test import TestCase
from django.http import HttpRequest
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.html import escape

from lists.models import Item, List
from lists.views import home_page
from lists.forms import ItemForm

class HomePageTest(TestCase):
    maxDiff =None
    def test_home_page_renders_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_uses_item_form(self):
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], ItemForm)

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

    def test_validation_errors_are_sent_back_to_homepage_template(self):
        response = self.client.post('/lists/new', data={'item_text':''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        expected_error = escape("You can't have an empty list item.")
        self.assertContains(response, expected_error)
    
    def test_validation_errors_end_up_on_lists_page(self):
        list_ = List.objects.create()
        response = self.client.post('/lists/%d/' % (list_.id, ),
                data = {'item_text': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')
        expected_error = escape("You can't have an empty list item.")
        self.assertContains(response, expected_error)

    def test_invalid_list_items_arent_saved(self):
        response = self.client.post('/lists/new', data={'item_text':''})
        self.assertEqual(List.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)
        
    def test_can_save_POST_request_to_existing_list(self):
        other = List.objects.create()
        correct = List.objects.create()
        response = self.client.post('/lists/%d/' % (correct.id,),
                   data = {"item_text": "new item for existing list"})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, "new item for existing list")
        self.assertEqual(new_item.list, correct)

    def test_POST_redirects_to_correct_list(self):
        other = List.objects.create()
        correct = List.objects.create()
        response = self.client.post('/lists/%d/' % (correct.id, ), 
                    data = {"item_text": "new item for existing list"})
        return self.assertRedirects(response, "/lists/%d/" % (correct.id, ))
