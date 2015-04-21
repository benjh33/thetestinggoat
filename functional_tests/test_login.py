from .base import FunctionalTest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException 

import time
import requests

class LoginTest(FunctionalTest):

    def get_new_persona_test_user(self):
        resp = requests.get('http://personatestuser.org/email')
        data = resp.json()
        return (data['email'], data['pass'])

    def test_login_with_persona(self):

        email, password = self.get_new_persona_test_user()
        print('testing login with fake user from "personatesuser.org/email"')
        print(email, password)

        self.browser.get(self.server_url)
        self.browser.find_element_by_id('login').click()

        self.switch_to_new_window('Mozilla Persona')

        self.browser.find_element_by_id(
                'authentication_email',
            ).send_keys(email)
        # finding that smaller window may show a mobile or desktop button.
        # desktop version has two buttons, so just looking for button tag no is no good
        try:
            element = self.browser.find_element_by_css_selector('.isDesktop.isStart')
        except NoSuchElementException as e:
            try:
                element = self.browser.find_element_by_css_selector('.continue')
                print('found .continue')
            except NoSuchElementException as e:
                self.fail("couldn't find a .next or .continue button")
        element.click()
        self.browser.find_element_by_id('authentication_password').send_keys(password)
        buttons = self.browser.find_elements_by_tag_name('button')
        for button in buttons:
            if button.is_displayed():
                if 'sign in' in button.text:
                    button.click()
                    break

        self.switch_to_new_window('To-Do')

        self.wait_for_element_with_id('logout')
        navbar = self.browser.find_element_by_css_selector('.navbar')
        self.assertIn(email, navbar.text)

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
                lambda b: b.find_element_by_id(element_id)
                )

