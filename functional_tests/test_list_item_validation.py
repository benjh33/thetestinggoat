from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from unittest import skip
import sys
import unittest
import time

from .base import FunctionalTest
from lists.forms import EMPTY_ITEM_ERROR, DUPLICATE_ITEM_ERROR

class ItemValidationTest(FunctionalTest):

    def test_cannot_submit_empty_list_item(self):

        # Edith tries to enter an empty item
        self.browser.get(self.server_url)
        self.get_item_input_box().send_keys('\n')

        # this should cause a problem
        error = self.get_error_element()
        self.assertTrue(error.is_displayed())
        self.assertEqual(error.text, EMPTY_ITEM_ERROR)

        # she tries again with actual text
        self.get_item_input_box().send_keys('Buy milk\n')
        self.check_for_row_in_list_table("1: Buy milk")

        # she tries again to enter an empty line and still there is an error
        self.get_item_input_box().send_keys('\n')
        error = self.get_error_element()
        self.assertTrue(error.is_displayed())

        # she can correct it by filling in some text
        self.get_item_input_box().send_keys('Make tea\n')
        self.check_for_row_in_list_table('1: Buy milk')
        self.check_for_row_in_list_table('2: Make tea')

    def test_cannot_add_duplicate_items(self):
        # Edith goes to the homepage and starts a list
        self.browser.get(self.server_url)
        self.get_item_input_box().send_keys('Buy wellies\n')
        self.check_for_row_in_list_table('1: Buy wellies')

        # accidentally, she tries to enter a duplicate item
        self.get_item_input_box().send_keys('Buy wellies\n')

        # she sees a helpful error message
        self.check_for_row_in_list_table('1: Buy wellies')
        error = self.get_error_element()
        self.assertFalse(error.is_displayed())
        self.assertEqual(error.text, DUPLICATE_ITEM_ERROR)

    def test_error_messages_are_cleared_on_input(self):
        # Edith enters a blank item
        self.browser.get(self.server_url)
        self.get_item_input_box().send_keys('\n')

        # Error pops up as expected
        error = self.get_error_element()
        self.assertTrue(error.is_displayed())

        # Edith starts to type 
        self.get_item_input_box().send_keys('a')
        
        # She is pleased to see the error disappears
        error = self.get_error_element()
        self.assertFalse(error.is_displayed())

    def get_error_element(self):
       return self.browser.find_element_by_css_selector('.has-error')
