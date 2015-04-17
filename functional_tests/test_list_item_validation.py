from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from unittest import skip
import sys
import unittest
import time

from .base import FunctionalTest

class ItemValidationTest(FunctionalTest):

    @skip
    def test_cannot_submit_empty_list_item(self):

        self.fail('write me!')
