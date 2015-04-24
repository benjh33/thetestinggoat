import unittest
from unittest.mock import patch, Mock

from django.test import TestCase
from django.http import HttpRequest
from django.utils.html import escape
from django.contrib.auth import get_user_model
User = get_user_model()

from lists.views import new_list
from lists.models import Item, List
from lists.forms import (
        ExistingListItemForm, ItemForm, 
        EMPTY_ITEM_ERROR, DUPLICATE_ITEM_ERROR
        )

class HomePageTest(TestCase):

    def test_home_page_renders_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_uses_item_form(self):
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], ItemForm)


class ListViewTest(TestCase):

    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get('/lists/%d/' % (list_.id, ))
        self.assertTemplateUsed(response, 'list.html')

    
    def test_passes_correct_list_to_template(self):
        list_1 = List.objects.create()
        list_2 = List.objects.create()
        response = self.client.get('/lists/%d/' % (list_2.id, ))
        self.assertEqual(response.context['list'], list_2)

    def test_displays_item_form(self):
        list_ = List.objects.create()
        response = self.client.get('/lists/%d/' % list_.id)
        self.assertIsInstance(response.context['form'], ExistingListItemForm )
        self.assertContains(response, 'name="text"')

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

    def test_can_save_POST_request_to_existing_list(self):
        other = List.objects.create()
        correct = List.objects.create()
        response = self.client.post('/lists/%d/' % (correct.id,),
                   data = {"text": "new item for existing list"})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, "new item for existing list")
        self.assertEqual(new_item.list, correct)

    def test_POST_redirects_to_list_view(self):
        other = List.objects.create()
        correct = List.objects.create()
        response = self.client.post('/lists/%d/' % (correct.id, ), 
                    data = {"text": "new item for existing list"})
        return self.assertRedirects(response, "/lists/%d/" % (correct.id, ))

    def post_invalid_input(self):
        list_ = List.objects.create()
        return self.client.post("/lists/%d/" % (list_.id,), 
                {'text':''})

    def test_for_invalid_input_nothing_saved_to_db(self):
        response = self.post_invalid_input()
        self.assertEquals(Item.objects.count(), 0)

    def test_for_invalid_input_renders_list_template(self):
        response = self.post_invalid_input()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')

    def test_for_invalid_input_passes_form_to_template(self):
        response = self.post_invalid_input()
        self.assertIsInstance(response.context['form'], ExistingListItemForm)

    def test_for_invalid_input_shows_error_on_page(self):
        response = self.post_invalid_input()
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_duplicate_item_validation_errors_end_up_on_lists_page(self):
        list_ = List.objects.create()
        Item.objects.create(list = list_, text = 'textey')
        response = self.client.post('/lists/%d/' % list_.id, 
                data = {'text': 'textey'})
        self.assertContains(response, escape(DUPLICATE_ITEM_ERROR))
        self.assertTemplateUsed(response, 'list.html')
        self.assertEqual(Item.objects.all().count(), 1)


class NewListViewIntegratedTest(TestCase):
    
    def test_saving_a_POST_request(self):
        self.client.post('/lists/new', 
                         {"text": "A new list item"})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, "A new list item")

    def test_for_invalid_input_doesnt_save_but_shows_errors(self):
        response = self.client.post('/lists/new', data={'text':''})
        self.assertEqual(List.objects.count(), 0)
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))
    
    def test_list_owner_is_saved_if_user_is_authenticated(self):
        request = HttpRequest()
        request.user = User.objects.create(email = 'a@b.com')
        request.POST['text'] = 'some text for a list'
        new_list(request)
        list_ = List.objects.first()
        self.assertEqual(list_.owner, request.user)
        
class MyListsTest(TestCase):

    """Tests involving users's personal lists"""
    def test_my_lists_url_renders_my_lists_template(self):
        User.objects.create(email = 'a@b.com')
        response = self.client.get("/lists/users/a@b.com/")
        self.assertTemplateUsed(response, "my_lists.html")

    def test_passes_correct_owner_to_template(self):
        User.objects.create(email = 'person@wrongowner.com')
        correct_user = User.objects.create(email = 'a@b.com')
        response = self.client.get('/lists/users/a@b.com/')
        self.assertEqual(response.context['owner'], correct_user)


@patch('lists.views.NewListForm')
class NewListViewUnitTest(unittest.TestCase):
    
    def setUp(self):
        self.request = HttpRequest()
        self.request.POST['text'] = "some new text"
        self.request.user = Mock()

    def test_passes_POST_data_to_NewListForm(self, mockNewListForm):
        new_list(self.request)
        mockNewListForm.assert_called_once_with(data=self.request.POST)

    def test_saves_form_with_owner_if_valid(self, mockNewListForm):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = True
        new_list(self.request)
        mock_form.save.assert_called_once_with(owner=self.request.user)

    @patch('lists.views.redirect')
    def test_redirects_to_form_returned_object_if_form_valid(self, 
            mock_redirect, mockNewListForm):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = True

        response = new_list(self.request)

        self.assertEqual(response, mock_redirect.return_value)
        mock_redirect.assert_called_once_with(
                mock_form.save.return_value)

    @patch('lists.views.render')
    def test_renders_home_template_with_form_if_form_invalid(self,
            mock_render, mockNewListForm):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = False
        
        response = new_list(self.request)

        self.assertEqual(response, mock_render.return_value)
        mock_render.assert_called_once_with(
                self.request, 'home.html', {'form': mock_form})

    def test_list_does_not_save_if_form_invalid(self, mockNewListForm):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = False
        response = new_list(self.request)
        self.assertFalse(mock_form.save.called)

