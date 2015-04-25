from selenium import webdriver
from .base import FunctionalTest

def quit_if_possible(browser):
    try: browser.quit()
    except: pass

class SharingTest(FunctionalTest):

    def test_logged_in_users_lists_are_saved_as_my_lists(self):

        # we have one logged in user
        email_1, pass_1 = (self.email, self.password)
        browser_1 = self.browser
        self.addCleanup(lambda: quit_if_possible(browser_1))

        # user 1's friend is also hanging out on the site
        browser_2 = webdriver.Firefox()
        self.addCleanup(lambda: quit_if_possible(browser_2))
        self.browser = browser_2
        self.get_new_persona_test_user()
        email_2, pass_2 = (self.email, self.password)
        self.create_pre_authenticated_session()
        
        # user 1 goes to homepage and starts a list
        self.browser = browser_1
        self.load_slow_browser()
        self.get_item_input_box().send_keys('Get help\n')
        
        # she notices a 'share this list' option
        share_box = self.wait_for_element_with_css('input[name=email]')
        self.assertEqual(
                share_box.get_attribute('placeholder'),
                "your-friend@example.com"
                )
