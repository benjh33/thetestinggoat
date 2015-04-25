import os
import sys
import requests
import time

from datetime import datetime
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.conf import settings
from django.contrib.auth import (BACKEND_SESSION_KEY, 
        SESSION_KEY, get_user_model)

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (NoSuchElementException, 
        WebDriverException)

from .server_tools import reset_database, create_session_on_server
from .management.commands.create_session import create_pre_authenticated_session

SCREEN_DUMP_LOCATION = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'screendumps')

DEFAULT_WAIT = 5

User = get_user_model()

class FunctionalTest(StaticLiveServerTestCase):

    def get_new_persona_test_user(self):
        """
        Attaches a qualified, random persona test user email and 
        password to the instance
        """
        resp = requests.get('http://personatestuser.org/email')
        data = resp.json()
        self.email = data['email']
        self.password = data['pass']

    @classmethod
    def setUpClass(cls):
        cls.email = None
        cls.load_tries = 0
        cls.get_new_persona_test_user(cls)
        #self.wait_for(lambda: self.assertIsNotNone(self.email))
        for arg in sys.argv:
            if 'liveserver' in arg:
                cls.server_host = arg.split('=')[1]
                cls.server_url = "http://" + arg.split("=")[1].split('@')[1]
                cls.against_staging = True
                return
        super().setUpClass()
        cls.against_staging = False
        cls.server_url = cls.live_server_url

    @classmethod
    def tearDownClass(cls):
        if cls.server_url == cls.live_server_url:
            super().tearDownClass()

    def setUp(self):
        if self.against_staging:
            reset_database(self.server_host)
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(DEFAULT_WAIT)

    def tearDown(self):
        if self._test_has_failed():
            if not os.path.exists(SCREEN_DUMP_LOCATION):
                os.makedirs(SCREEN_DUMP_LOCATION)
            for ix, handle in enumerate(self.browser.window_handles):
                self._windowid = ix
                self.browser.switch_to_window(handle)
                self.take_screenshot()
                self.dump_html()
        self.browser.quit()
        super().tearDown()

    def _test_has_failed(self):
        for method, error in self._outcome.errors:
            if error:
                return True
        return False

    def take_screenshot(self):
        filename = self._get_filename() + ".png"
        print('screenshotting to', filename)
        self.browser.get_screenshot_as_file(filename)

    def dump_html(self):
        filename = self._get_filename() + '.html'
        print('dumping HTML to', filename)
        with open(filename, 'w') as f:
            f.write(self.browser.page_source)

    def _get_filename(self):
        timestamp = datetime.now().isoformat().replace(':', '.')[:19]
        return '{folder}/{classname}.{method}-window{windowid}-{timestamp}'.format(
                folder=SCREEN_DUMP_LOCATION,
                classname=self.__class__.__name__,
                method=self._testMethodName,
                windowid=self._windowid,
                timestamp=timestamp)

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
        navbar = self.wait_for_element_with_css('.navbar') 
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
    
    def wait_for_element_with_css(self, selector):
        return WebDriverWait(self.browser, timeout=10).until(
                lambda b: b.find_element_by_css_selector(selector),
                '''Could not find element with css selector {}. 
                Page text was:\n{}'''.format(
                    selector, self.browser.find_element_by_tag_name('body').text
                    )
                )

    def wait_for_element_with_id(self, element_id):
        return WebDriverWait(self.browser, timeout=30).until(
                lambda b: b.find_element_by_id(element_id),
                'Could not find element with id {}. Page text was:\n{}'.format(
                    element_id, self.browser.find_element_by_tag_name('body').text
                    )
                )

    def wait_for(self, function_with_assertion, timeout=DEFAULT_WAIT):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                return function_with_assertion()
            except (AssertionError, WebDriverException):
                time.sleep(0.1)
        return function_with_assertion()
    
    def create_pre_authenticated_session(self):
        session_key = None
        if self.against_staging:
            session_key = create_session_on_server(self.server_host, 
                    self.email)
            print(session_key)
        else:
            session_key = create_pre_authenticated_session(self.email)
        self.wait_for(lambda: self.assertIsNotNone(session_key))
        # to set a cookie, we need to visit the domain
        # 404 loads fastest
        self.load_slow_browser("/404_no_such_page/")
        self.browser.add_cookie(dict(
            name=settings.SESSION_COOKIE_NAME,
            value=session_key,
            path="/"))

    def load_slow_browser(self, path=''):
        try:
            self.load_tries += 1
            self.browser.get(self.server_url + path)
            WebDriverWait(self.browser, 1).until(
                lambda x: self.browser.current_url != 'about:blank')
        finally:
            if self.load_tries < 5 and self.browser.current_url=='about:blank':
                self.load_slow_browser(path)
            elif self.browser.current_url == 'about:blank':
                self.fail("could not load page")
            self.load_tries = 0 
