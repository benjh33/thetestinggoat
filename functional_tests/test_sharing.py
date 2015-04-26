from selenium import webdriver
from .base import FunctionalTest
from .home_and_list_pages import HomePage

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
        list_page = HomePage(self).start_new_list('Get help')

        # she notices a 'share this list' option
        share_box = list_page.get_share_box()
        self.assertEqual(
                share_box.get_attribute('placeholder'),
                "your-friend@example.com"
                )

        # she shares her list and sees the page updates with 
        # her friend's email address
        list_page.share_list_with(email_2)
        
        # now user two goes to the lists page
        self.browser = browser_2
        HomePage(self).go_to_home_page().go_to_my_lists_page()

        # he see's the lists user 1 has shared with him
        self.browser.find_element_by_link_text('Get help').click()

        # on the list page, user 2 can see it's user 1's page
        self.wait_for(lambda: self.assertEqual(
            list_page.get_list_owner(),
            email_1))

        # he adds an item to the list
        list_page.add_new_item('Hi {}!'.format(email_1))

        # when user 1 refreshes the page, she sees the new list item
        self.browser = browser_1
        self.browser.refresh()
        list_page.wait_for_new_item_in_list('Hi {}!'.format(email_1))
