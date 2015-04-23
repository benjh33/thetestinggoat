from django.conf import settings
from django.contrib.auth import get_user_model

from .base import FunctionalTest
from .server_tools import create_session_on_server
from .management.commands.create_session import create_pre_authenticated_session

User = get_user_model()

class MyListsTest(FunctionalTest):

    def create_pre_authenticated_session(self, email):
        if self.against_staging:
            session_key = create_session_on_server(self.server_host, email)
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
        
        self.get_new_persona_test_user()
        self.browser.get(self.server_url)
        self.wait_to_be_logged_out(self.email)

        # Edith is a logged in user
        self.create_pre_authenticated_session(self.email)

        self.browser.get(self.server_url)
        self.wait_to_be_logged_in(self.email)



