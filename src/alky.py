#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import base64
import boto.s3
import boto.sts
import os
import requests
import urllib
import xml.etree.ElementTree as ET

class Alky:
    def __init__(self, **kwargs):
        """Initialise an Alky object

        Keyword Arguemts:
        username -- username **with fqdn** to login with
        password -- corresponding password
        """
        self.username = kwargs.pop('username')
        self.password = kwargs.pop('password')
        self.mfa_code = kwargs.pop('mfa_code')
        self.role = kwargs.pop('role')
        self.principal = kwargs.pop('principal')

        self.region = kwargs.pop('region')

        self.google_accounts_url = "https://accounts.google.com/o/saml2/initsso?idpid=%s&spid=%s&forceauthn=false" % (kwargs.pop('idp'),
                                                                                                                      kwargs.pop('sp'))
        if kwargs:
            raise ValueError, ("Extraneous keys passed: %s" % kwargs.keys())

    def key(self):
        """Return a key object"""
        self.session = self.login_to_google()
        self.sts = self.login_to_sts(self.region)

        saml = self.parse_google_saml()

        access_key, secret_key, session_token = self.get_tokens(saml, self.role, self.principal)
        return {
            'aws': {
                'access_key': access_key,
                'secret_key': secret_key,
                'session_token': session_token
            }
        }

    def login_to_google(self):
        """Create a google login context"""
        authentication_url = 'https://accounts.google.com/ServiceLoginAuth'

        session = requests.Session()
        google_session = session.get(self.google_accounts_url)

        s = str(google_session.headers.get('X-Auto-Login','none'))
        s = urllib.unquote(s).decode('utf8')
        result = urllib.unquote(s).decode('utf8')
        identityurl = result[result.index('https'):]

        galx = google_session.cookies['GALX']

        session.headers['User-Agent'] = 'AWS Sign-in'

        payload = {
            'Email': self.username,
            'GALX': galx,
            'Passwd': self.password,
            'PersistentCookie': 'yes',
            '_utf8': '☃',
            'bgresponse': 'js_disabled',
            'checkConnection': 'youtube:206:1',
            'checkedDomains': 'youtube',
            'continue': self.google_accounts_url,
            'dnConn': '',
            'hl': 'en',
            'pstMsg': 1,
            'signIn': 'Sign in'
        }

        google_session = session.post(authentication_url, data=payload)

        set_cookie = google_session.headers.get("Set-Cookie","none")

        try:
            tl = set_cookie.split(";")[0].split("TC=")[1]
        except:
            raise StandardError, 'Incorrect login credentials'

        if (google_session.url == authentication_url) or (google_session.status_code == 500):
            raise StandardError, 'Could not get a session, incorrect login credentials'


        challenge_url = google_session.url.split("?")[0]
        challenge_id  = challenge_url.split("totp/")[1]

        decoded = BeautifulSoup(google_session.text, 'html.parser')

        for inputtag in decoded.find_all('input'):
            if(inputtag.get('name') == 'gxf'):
                gxf = inputtag.get('value')

        if not gxf:
            raise StandardError, "Could not find gfx tag"

        payload = {
            'Pin': self.mfa_code,
            'TL': tl,
            'TrustDevice': 'on',
            'challengeId': challenge_id,
            'challengeType': '6',
            'checkConnection': 'youtube:189:1',
            'checkDomains': 'youtube',
            'continue': self.google_accounts_url,
            'gxf': gxf,
            'pstMsg': 1,
            'sarp': 1
        }

        google_session = session.post(challenge_url, data=payload)

        if (google_session.url == challenge_url) or (google_session.status_code == 500):
            print google_session.text
            raise StandardError, 'Could not get a session, incorrect MFA'

        print session
        return session

    def parse_google_saml(self):
        """Load and parse saml from google"""
        response = self.session.get(self.google_accounts_url)

        parsed = BeautifulSoup(response.text, 'html.parser')
        saml_element = parsed.find('input', {'name':'SAMLResponse'})

        if not saml_element:
            raise StandardError, 'Could not get a SAML reponse, check credentials'

        return saml_element['value']

    def login_to_sts(self, region):
        """Create an STS context via STS"""
        return boto.sts.connect_to_region(region)

    def get_tokens(self, saml, role, principal):
        """Load and parse tokes from AWS STS"""
        token = self.sts.assume_role_with_saml(role, principal, saml, duration_seconds=900)

        return token.credentials.access_key, token.credentials.secret_key, token.credentials.session_token


def generate_key(event, context):
    username = event.get('username')
    password = event.get('password')
    mfa_code = event.get('mfa_code')

    region = event.get('region', 'eu-west-1')

    # The following, we expect, to come from $stageVariables
    idp = event.get('idp', 'C03sswb4h')
    sp  = event.get('sp', '553442466309')
    role = event.get('role', 'arn:aws:iam::810385116814:role/SSOTestRole')
    principal = event.get('principal', 'arn:aws:iam::810385116814:saml-provider/jamescondron_googleSAML')

    # Duplication is to avoid defaulting values in the class
    # - thats logic we shouldn't be doing there
    return Alky(username=username,
                password=password,
                mfa_code=mfa_code,
                idp=idp,
                sp=sp,
                region=region,
                role=role,
                principal=principal).key()

if __name__ == '__main__':
    k = generate_key(
        {'username': os.environ.get('ALKY_USERNAME'),
         'password': os.environ.get('ALKY_PASSWORD'),
         'mfa_code': os.environ.get('ALKY_MFA_CODE')
        },
        {}
    )
    print(k)
