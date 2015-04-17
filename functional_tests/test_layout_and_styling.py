from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from unittest import skip
import sys
import unittest
import time

from .base import FunctionalTest

class LayoutAndStylingTest(FunctionalTest):

    def test_layout_and_styling(self):
        self.browser.get(self.server_url)
        self.browser.set_window_size(1024, 768)

        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('testing...')
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width']//2,
            512, delta = 5)
