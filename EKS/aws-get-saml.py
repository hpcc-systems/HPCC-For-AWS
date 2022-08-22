#!/usr/bin/env python3

import os
import sys
import boto3
import cryptography
import requests
import getpass
import base64
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from os.path import expanduser
from requests_ntlm import HttpNtlmAuth
import logging
import configparser
import urlparse2

logging.basicConfig(level=logging.INFO)
logging.getLogger('botocore').setLevel(logging.ERROR)

##########################################################################
# Variables

# region: The default AWS region that this script will connect
# to for all API calls
region = os.environ.get('AWS_REGION') or 'us-west-2'

# output format: The AWS CLI output format that will be configured in the
# saml profile (affects subsequent CLI calls)
#outputformat = 'json'
outputformat = 'text'

# awsconfigfile: The file where this script will store the temp
# credentials under the saml profile
#awsconfigfile = '/.aws/credentials'
#awsconfigfile = '/work/AWS/credentials'
awsconfigfile = '/.aws/credentials'

# SSL certificate verification: Whether or not strict certificate
# verification is done, False should only be used for dev/test
sslverification = True

# idpentryurl: The initial URL that starts the authentication process.
idpentryurl = 'https://federation.reedelsevier.com/adfs/ls/IdpInitiatedSignOn.aspx?loginToRp=urn:amazon:webservices'
idpentrygovcloudurl = 'https://federation.reedelsevier.com/adfs/ls/IdpInitiatedSignOn.aspx?loginToRp=urn:amazon:webservices:govcloud'

# Duration in seconds
raw_duration = os.environ.get('ACCESS_DURATION') or 3600
duration = int(raw_duration)

amigovcloud = os.environ.get('GOVCLOUD') or False

##########################################################################

# Get the federated credentials from the user
role_match = os.environ.get('ADFS_ROLE') or 'ADFS-HPCCPlatformTeam'
print ("role to match: " + role_match)

#username = os.environ.get('LDAP_USER') or os.environ.get('USERNAME') or os.environ.get('USER')
#password = os.environ.get('LDAP_PASSWORD') or os.environ.get('PASS')
#username = "svc-hpccdev"
#password = "neCrop{0ga3t\ophI"
username = os.environ.get('RISK_USERNAME')
password = os.environ.get('RISK_PASSWORD')

if not username:
    username = input("Username:")

if not password:
    password = getpass.getpass('Enter password for [%s]: ' % username)

if '\\' not in username:
    username = 'RISK\\' + username

# Initiate session handler
session = requests.Session()
# Default User-Agent string does not correctly enable the NTLM authentication
# Masquerade as Firefox to make server behave as we want
#session.headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
#session.headers['User-Agent'] = 'Mozilla/5.0'
session.headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'

# Programatically get the SAML assertion
# Set up the NTLM authentication handler by using the provided credential
session.auth = HttpNtlmAuth(username, password)  # , session)

# Opens the initial AD FS URL and follows all of the HTTP302 redirects
if amigovcloud:
    response = session.get(
        idpentrygovcloudurl, verify=sslverification, allow_redirects=True)
else:
    response = session.get(
        idpentryurl, verify=sslverification, allow_redirects=True)

# Overwrite and delete the credential variables, just for safety
del username
del password

# Decode the response and extract the SAML assertion
#soup = BeautifulSoup(response.text.decode('utf8'))
databytes = response.text.encode('utf-8')

soup = BeautifulSoup(response.text, "html.parser")
assertion = ''

# Look for the SAMLResponse attribute of the input tag (determined by
# analyzing the debug print lines above)
for inputtag in soup.find_all('input'):
    if(inputtag.get('name') == 'SAMLResponse'):
        assertion = inputtag.get('value')

if not assertion:
    logging.critical('Unable to retrieve SAML assertion')
    sys.exit(1)

# Parse the returned assertion and extract the authorized roles
awsroles = []
root = ET.fromstring(base64.b64decode(assertion))

for saml2attribute in root.iter('{urn:oasis:names:tc:SAML:2.0:assertion}Attribute'):
    if (saml2attribute.get('Name') == 'https://aws.amazon.com/SAML/Attributes/Role'):
        for saml2attributevalue in saml2attribute.iter('{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue'):
            # Note the format of the attribute value should be role_arn,principal_arn
            # but lots of blogs list it as principal_arn,role_arn so let's reverse
            # them if needed
            f1, f2 = saml2attributevalue.text.split(',')
            logging.debug('Found SAML role: %s - %s' % (f1, f2))
            if 'saml-provider' in f1:
                awsroles.append((f2, f1))
            else:
                awsroles.append((f1, f2))

# Write the AWS STS token into the AWS credential file
home = expanduser("~")
filename = home + awsconfigfile

# Read in the existing config file
config = configparser.RawConfigParser()
config.read(filename)

# Use the assertion to get an AWS STS token using Assume Role with SAML
conn = boto3.client('sts')
access_keys = dict()

for role, principal in awsroles:
    account_id, role_name = role.split(':')[-2:]
    if role_name.startswith('role/'):
        role_name = role_name[5:]
    if role_name != role_match:
        #print("role name : " + role_name)
        continue
    token = conn.assume_role_with_saml(
        RoleArn=role, PrincipalArn=principal, SAMLAssertion=assertion, DurationSeconds=duration)
    if amigovcloud:
        iam = boto3.client('iam', aws_access_key_id=token['Credentials']['AccessKeyId'],
                    aws_secret_access_key=token['Credentials']['SecretAccessKey'],
                    aws_session_token=token['Credentials']['SessionToken'], region_name=region)
    else:
        iam = boto3.client('iam', aws_access_key_id=token['Credentials']['AccessKeyId'],
                    aws_secret_access_key=token['Credentials']['SecretAccessKey'],
                    aws_session_token=token['Credentials']['SessionToken'])
    alias = iam.list_account_aliases()
    account_names = alias.get('AccountAliases', [])
    if account_names:
        logging.debug('Mapping account #%s to [%s]' % (
            account_id, account_names[0]))
        account_id = account_names[0]
    access_keys[account_id] = token

# Put the credentials into a specific profile instead of clobbering
# the default credentials

for account, token in access_keys.items():
    if not config.has_section(account):
        config.add_section(account)

    config.set(account, '### role', role_match)
    config.set(account, '### expiration', '{0}'.format(
        token['Credentials']['Expiration']))
    config.set(account, 'output', outputformat)
    config.set(account, 'region', region)
    config.set(account, 'aws_access_key_id',
               token['Credentials']['AccessKeyId'])
    print("Access Key Id: " +  token['Credentials']['AccessKeyId'])
    config.set(account, 'aws_secret_access_key',
               token['Credentials']['SecretAccessKey'])
    print("Secrete Access Key: " +  token['Credentials']['SecretAccessKey'])
    config.set(account, 'aws_session_token',
               token['Credentials']['SessionToken'])
    print("Expiration: " +  format(token['Credentials']['Expiration']) + "\n")

# Rewrite the updated config file
with open(filename, 'w+') as configfile:
    config.write(configfile)
#logging.info(
#    'Updated AWS credentials file [%s] with %d profiles', filename, len(access_keys))
