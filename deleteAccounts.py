#!/usr/bin/env python3
"""
Andrew Villeneuve 2025
Tool to remove all accounts in the Trailhead sandbox to reset the evaluation
"""

### Config ###

CREDENTIALS_FILE='.creds'

### Includes ###

import simple_salesforce
import configparser

### Implementation ###

config = configparser.ConfigParser()
config.read(CREDENTIALS_FILE)
inst = config['sandbox']['Endpoint']
token = config['sandbox']['Token']
print("Got Credentials")

# Note that the security token needs to be passed in as 'session_id',
# not 'security_token'
sf = simple_salesforce.Salesforce(instance=inst, session_id=token)
print("Connected")

acclist = sf.query("SELECT Id, AccountNumber, Name FROM Account")
print(f"Found {acclist['totalSize']} accounts in the sandbox")

for rec in acclist['records']:
	try:
		sf.Account.delete(rec['Id'])
	except simple_salesforce.exceptions.SalesforceMalformedRequest as e:
		print(f"Unable to delete record {rec['Id']} because {e}")

print("Done")