from django.conf import settings
from django.contrib.auth import (BACKEND_SESSION_KEY, 
        SESSION_KEY, get_user_model)
from django.contrib.sessions.backends.db import SessionStore

from .base import FunctionalTest

User = get_user_model()

class MyListsTest(FunctionalTest):

    def test_logged_in_users_lists_are_saved_as_my_lists(self):
        self.get_new_persona_test_user()
        self.browser.get(self.server_url)
        self.wait_to_be_logged_out(self.email)

        # Edith is a logged in user
        self.create_pre_authenticated_session(self.email)

        self.browser.get(self.server_url)
        self.wait_to_be_logged_in(self.email)



