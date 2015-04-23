import subprocess

from os import path

THIS_FOLDER = path.dirname(path.abspath(__file__))
'''
This file is used exclusively for operating on the staging db and then 
deleting it. "create_session_on_server" and "reset_database" are functions
in functional_tools/fabfile.py that call the server's ./manage.py from
the dev machine. 
'''
def create_session_on_server(host, email, user):
    return subprocess.check_output(
            [
                'fab',
                'create_session_on_server:email={}'.format(email),
                '--host={}'.format(host),
                '--hide=everything,status',
                '--user={}'.format(user)
                ],
            cwd=THIS_FOLDER,
       ).decode().strip()

def reset_database(host, user):
    print(host)
    subprocess.check_call(
            [
                'fab', 
                'reset_database',
                '--host={}'.format(host),
                '--user={}'.format(user),
            ],
            cwd=THIS_FOLDER)



