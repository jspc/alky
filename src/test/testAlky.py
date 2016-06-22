import unittest
import responses
import os

from alky import Alky

class AlkyTest(unittest.TestCase):

    def setUp(self):
        self.fixtures_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'fixtures')

        self.username = 'billy.goat@ft.com'
        self.password = 'password'
        self.idp = 'some-string'
        self.sp  = 'another-string'
        self.role = 'arn::foo'
        self.principal = 'arn::bar'
        self.region = 'eu-west-1'

        self.alky = Alky(username=self.username,
                         password=self.password,
                         idp=self.idp,
                         sp=self.sp,
                         role=self.role,
                         principal=self.principal,
                         region=self.region
        )

    def tearDown(self):
        True

    def test_username(self):
        assert(self.alky.username == self.username)

    def test_password(self):
        assert(self.alky.password == self.password)

    def test_url(self):
        assert(self.alky.google_accounts_url == "https://accounts.google.com/o/saml2/initsso?idpid=some-string&spid=another-string&forceauthn=false")

    def test_role(self):
        assert(self.alky.role == self.role)

    def test_principal(self):
        assert(self.alky.principal == self.principal)

    def test_region(self):
        assert(self.alky.region == self.region)

    @responses.activate
    def test_login_to_google(self):
        def get_session_callback(request):
            body = open(os.path.join(self.fixtures_path, 'google_accounts_url_body')).read().strip()
            headers = open(os.path.join(self.fixtures_path, 'google_accounts_url_headers')).read().strip()

            print body
            print headers

            return (200, headers, body)

        def post_session_callback(request):
            body = open(os.path.join(self.fixtures_path, 'google_accounts_session_body')).read().strip()
            headers = open(os.path.join(self.fixtures_path, 'google_accounts_session_headers')).read().strip()
            return (200, headers, body)

        responses.add_callback(responses.GET,
                      self.alky.google_accounts_url,
                      content_type='application/html',
                      callback=get_session_callback)

        responses.add_callback(responses.POST,
                      self.alky.google_accounts_url,
                      content_type='application/html',
                      callback=post_session_callback)

        assert(self.alky.login_to_google() != None)
