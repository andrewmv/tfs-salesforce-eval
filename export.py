#!/usr/bin/env python3
"""
Andrew Villeneuve 2025
Export Account data from TrailHead Playground to local CSV
"""

### Config ###

CREDENTIALS_FILE='.creds'
BULK_API=True

### Includes ###

import sys
import csv
import simple_salesforce
import configparser

### Vars ###

bulk_data = []

### Implementation ###

def getCreds():
	config = configparser.ConfigParser()
	config.read(CREDENTIALS_FILE)
	return (config['sandbox']['Endpoint'], config['sandbox']['Token'])

def main():
	# Ensure the user provided the target CSV file name as an argument
	try:
		datafile = sys.argv[1]
	except IndexError:
		print(f"Usage: {sys.argv[0]} <filename.csv>")
		sys.exit(2)

	# Read Salesforce API credentials from disk
	try:
		(inst, token) = getCreds()
	except (FileNotFoundError, KeyError):
		print(f"Error: Couldn't read the credentials from file {CREDENTIALS_FILE}")
		sys.exit(1)

	# Connect to SalesForce/TrailHead
	# Note that the security token needs to be passed in as 'session_id',
	# not 'security_token', which is only used for JWT tokens
	session = simple_salesforce.Salesforce(instance=inst, session_id=token)
	print("Connected!")

	# Query data
	query = 'SELECT Name,BillingStreet,BillingCity,BillingCountry,BillingPostalCode,BillingState,ShippingStreet,ShippingCity,ShippingCountry,ShippingPostalCode,ShippingState,NumberOfEmployees,Phone,AnnualRevenue FROM Account'
	try:
		result = session.bulk2.Account.download(query, path='out/', max_records=500)
		for i, job in enumerate(result):
			print(f"Batch {i+1} of {len(result)}:")
			print(job)
	except Exception as e:
		print(f"Exception with bulk export {e}")

if __name__ == "__main__":
	main()

