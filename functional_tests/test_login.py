from .base import FunctionalTest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import InvalidSelectorException
import time

class LoginTest(FunctionalTest):

    def test_login_with_persona(self):
        self.browser.get(self.server_url)
        self.browser.find_element_by_id('login').click()

        self.switch_to_new_window('Mozilla Persona')

        self.browser.find_element_by_id(
                'authentication_email',
            ).send_keys('edith@mockmyid.com')
        try:
            element = self.browser.find_element_by_css_selector('.next')
        except InvalidSelectorException:
            element = self.browser.find_element_by_css_selector('.continue')


        self.switch_to_new_window('To-Do')

        self.wait_for_element_with_id('logout')
        navbar = self.browser.find_element_by_css_selector('.navbar')
        self.assertIn('edith@mockmyid.com', navbar.text)

    def switch_to_new_window(self, text_in_title):
        retries = 60
        while retries > 0:
            for handle in self.browser.window_handles:
                self.browser.switch_to_window(handle)
                if text_in_title in self.browser.title:
                    return
            retries -= 1
            time.sleep(0.5)
        self.fail('could not find window %s' % text_in_title)


    def wait_for_element_with_id(self, element_id):
        WebDriverWait(self.browser, timeout=30).until(
                lambda b: b.find_element_by_id(element_id)
                )

