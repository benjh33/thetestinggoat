import requests
import sys

from accounts.models import ListUser

class PersonaAuthenticationBackend(object):

    def authenticate(self, assertion):

        data = {'assertion': assertion, 'audience': 'localhost'}
        print('sending to Mozilla', data, file=sys.stderr)
        resp = requests.post('https://verifier.login.persona.org/verify', data=data)
        print('got', resp.content, file=sys.stderr)

        # did verifier respond
        if resp.ok:
            # parse response
            verification_data = resp.json()

            # check if assertion was valid
            if verification_data['status'] == 'okay':
                email = verification_data['email']
                try:
                    return self.get_user(email)
                except ListUser.DoesNotExist:
                    return ListUser.objects.create(email = email)

    def get_user(self, email):
        return ListUser.objects.get(email = email)
    


