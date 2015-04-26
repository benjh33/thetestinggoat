from .base import FunctionalTest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException 

import time
import requests

class LoginTest(FunctionalTest):

    def test_login_with_persona(self):

        #self.get_new_persona_test_user()
        print('testing login with fake user from "personatesuser.org/email"')
        print(self.email, self.password)

        self.load_page()
        self.browser.find_element_by_id('id_login').click()

        self.switch_to_new_window('Mozilla Persona')

        self.browser.find_element_by_id(
                'authentication_email',
            ).send_keys(self.email)
        try:
            element = self.browser.find_element_by_css_selector('.isDesktop.isStart')
        except NoSuchElementException:
            try:
                element = self.browser.find_element_by_css_selector('.continue')
                print('found .continue')
            except NoSuchElementException as e:
                self.fail("couldn't find a .next or .continue button")
        element.click()
        self.browser.find_element_by_id(
                'authentication_password').send_keys(self.password)
        buttons = self.browser.find_elements_by_tag_name('button')
        for button in buttons:
            if button.is_displayed():
                if 'sign in' in button.text:
                    button.click()
                    break
        # browser goes back to  site after logging in
        self.switch_to_new_window('To-Do')
        # she sees that the login button disappears and her email is there
        self.wait_to_be_logged_in()
        # refreshes to see what happens
        self.browser.refresh()
        self.wait_to_be_logged_in()
        # clicks 'logout' to see what happens
        self.browser.find_element_by_id('id_logout').click()
        self.wait_to_be_logged_out()
        # she's logged out. refresh to test. still logged out
        self.browser.refresh()
        self.wait_to_be_logged_out()

