from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.conf import settings
from django.contrib.auth import (BACKEND_SESSION_KEY, 
        SESSION_KEY, get_user_model)
from django.contrib.sessions.backends.db import SessionStore
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException 

import sys
import requests

User = get_user_model()

class FunctionalTest(StaticLiveServerTestCase):

    def create_pre_authenticated_session(self, email):
        user = User.objects.create(email = email)
        session = SessionStore()
        session[SESSION_KEY] = user.pk
        session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
        session.save()
        ## to get a cookie we need to visit the domain
        ## 404 pages load quick
        self.browser.get(self.server_url + "/404_no_such_page/")
        self.browser.add_cookie(dict(
            name=settings.SESSION_COOKIE_NAME,
            value=session.session_key,
            path="/"
        ))

    def get_new_persona_test_user(self):
        resp = requests.get('http://personatestuser.org/email')
        data = resp.json()
        self.email = data['email']
        self.password = data['pass']

    @classmethod
    def setUpClass(cls):
        for arg in sys.argv:
            if 'liveserver' in arg:
                cls.server_url = "http://" + arg.split("=")[1]
                return
        super().setUpClass()
        cls.server_url = cls.live_server_url

    @classmethod
    def tearDownClass(cls):
        if cls.server_url == cls.live_server_url:
            super().tearDownClass()

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(1)

    def tearDown(self):
        self.browser.quit()

    def check_for_row_in_list_table(self, row_text):
        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertIn(row_text, [row.text for row in rows])

    def get_item_input_box(self):
        return self.browser.find_element_by_id('id_text')


    def wait_to_be_logged_in(self, email=None):
        self.wait_for_element_with_id('id_logout')
        navbar = self.browser.find_element_by_css_selector('.navbar')
        self.assertIn(self.email, navbar.text)

    def wait_to_be_logged_out(self, email=None):
        self.wait_for_element_with_id('id_login')
        navbar = self.browser.find_element_by_css_selector('.navbar')
        self.assertNotIn(self.email, navbar.text)
    
    def switch_to_new_window(self, text_in_title):
        retries = 60
        while retries > 0:
            for handle in self.browser.window_handles:
                self.browser.switch_to_window(handle)
                if text_in_title in self.browser.title:
                    print('found it: %s' % (self.browser.title,) )
                    return
            retries -= 1
            time.sleep(0.5)
        self.fail('could not find window %s' % text_in_title)
    
    def wait_for_element_with_id(self, element_id):
        WebDriverWait(self.browser, timeout=30).until(
                lambda b: b.find_element_by_id(element_id),
                'Could not find element with id {}. Page text was:\n{}'.format(
                    element_id, self.browser.find_element_by_tag_name('body').text
                    )
                )


