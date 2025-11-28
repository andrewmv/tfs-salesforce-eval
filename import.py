#!/usr/bin/env python3
"""
Andrew Villeneuve 2025
Ingest provided CSV into TrailHead Playground as Account records
"""

### Config ###

CREDENTIALS_FILE='.creds'

### Includes ###

import sys
import csv
import simple_salesforce
import configparser

### Implementation ###

def getCreds():
	config = configparser.ConfigParser()
	config.read(CREDENTIALS_FILE)
	return (config['sandbox']['Endpoint'], config['sandbox']['Token'])

def parseFile(datafile):
	with open(datafile, r, newline='') as f:
		reader = csv.DictReader(f)
		return reader


def main():
	try:
		(inst, token) = getCreds()
	except FileNotFound, KeyError:
		print(f"Error: Couldn't read the credentials from file {CREDENTIALS_FILE}")
		sys.exit(1)

	try:
		datafile = sys.argv[1]
	except IndexError:
		print(f"Usage: {sys.argv[0]} <filename.csv>")
		sys.exit(2)

	data = parseFile(datafile)

	# Note that the security token needs to be passed in as 'session_id',
	# not 'security_token'
	session = simple_salesforce.Salesforce(instance=inst, session_id=token)
	print("Connected!")

if __name__ == "__main__":
	main()
