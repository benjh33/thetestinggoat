from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from unittest import skip
import sys
import unittest
import time

from .base import FunctionalTest

class ItemValidationTest(FunctionalTest):

    def test_cannot_submit_empty_list_item(self):

        # Edith tries to enter an empty item
        self.browser.get(self.server_url)
        self.get_item_input_box().send_keys('\n')

        # this should cause a problem
        error = self.browser.find_element_by_css_selector('.has-error')
        self.assertEqual(error.text, "You can't have an empty list item.")

        # she tries again with actual text
        self.get_item_input_box().send_keys('Buy milk\n')
        self.check_for_row_in_list_table("1: Buy milk")

        # she tries again to enter an empty line and still there is an error
        self.get_item_input_box().send_keys('\n')
        error = self.browser.find_element_by_css_selector('.has-error')
        self.assertEqual(error.text, "You can't have an empty list item.")

        # she can correct it by filling in some text
        self.get_item_input_box().send_keys('Make tea\n')
        self.check_for_row_in_list_table('1: Buy milk')
        self.check_for_row_in_list_table('2: Make tea')
