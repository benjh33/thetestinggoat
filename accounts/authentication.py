from django.contrib.auth import get_user_model
from django.conf import settings
import logging
import requests

logger = logging.getLogger(__name__)

PERSONA_VERIFY_URL = 'https://verifier.login.persona.org/verify'

User = get_user_model()

class PersonaAuthenticationBackend(object):

    def authenticate(self, assertion):
        logging.warning('entering authenticate function')
        response = requests.post(PERSONA_VERIFY_URL, 
                data={'assertion': assertion, 'audience': settings.DOMAIN})
        logging.warning('got response from persona')
        logging.warning(response.content.decode())
        if response.ok and response.json()['status'] == 'okay':
            email = response.json()['email']
            try:
                return User.objects.get(email = email)
            except User.DoesNotExist:
                return User.objects.create(email = email)
        else:
            logger.warning(
                    'Persona says no. Json was {}'.format(response.json())
                    )


    def get_user(self, email):
        try:
            return User.objects.get(email = email)
        except User.DoesNotExist:
            return None

