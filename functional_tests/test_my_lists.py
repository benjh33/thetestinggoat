from django.conf import settings
from django.contrib.auth import get_user_model

from .base import FunctionalTest
from .server_tools import create_session_on_server
from .management.commands.create_session import create_pre_authenticated_session

User = get_user_model()

class MyListsTest(FunctionalTest):

    def create_pre_authenticated_session(self, email):
        if self.against_staging:
            session_key = create_session_on_server(self.server_host, 
                    email)
        else:
            session_key = create_pre_authenticated_session(email)

        ## to set cookie we need to first visit domain
        ## 404 loads the quickest
        self.browser.get(self.server_url + "/404_does_not_exist/")
        self.browser.add_cookie(dict(
            name=settings.SESSION_COOKIE_NAME,
            value=session_key,
            path='/'
            ))           

    def test_logged_in_users_lists_are_saved_as_my_lists(self):
        
        # Edith is a logged in user
        self.create_pre_authenticated_session(self.email)

        self.browser.get(self.server_url)
        self.get_item_input_box().send_keys("Reticulate splines\n")
        self.get_item_input_box().send_keys("Imanentize eschaton\n")
        first_list_url = self.browser.current_url

        # she notices 'my lists' link for the first time
        self.browser.find_element_by_link_text('My lists').click()

        # she sees her list is there, named according to first item
        self.browser.find_element_by_link_text('Reticulate splines').click()
        self.wait_for(
                lambda: self.assertEqual(self.browser.current_url, first_list_url)
                )

        # she decides to start another list, just to see
        self.browser.get(self.server_url)
        self.get_item_input_box().send_keys('Click cows\n')
        second_list_url = self.browser.current_url

        # under "My lists" here new list appears
        self.browser.find_element_by_link_text('My lists').click()
        self.browser.find_element_by_link_text('Click cows').click()
        self.assertEqual(self.browser.current_url, second_list_url)

        # she logs out "my list option disappears
        self.browser.find_element_by_id('id_logout').click()
        self.assertEqual(
                self.browser.find_elements_by_link_text('My lists'),
                [])




