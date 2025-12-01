#!/usr/bin/env python3
"""
Andrew Villeneuve 2025
Export Account data from TrailHead Playground to local CSV

The user will need to oauth authenticate and place the resulting instance
endpoint and security token in the .creds file to connect to SalesForce
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

def main():
	# Ensure the user provided the target CSV file name as an argument
	try:
		outfile = sys.argv[1]
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
	#
	# Note that the security token needs to be passed in as 'session_id',
	# not 'security_token', which is only used for JWT tokens
	session = simple_salesforce.Salesforce(instance=inst, session_id=token)
	print("Connected!")

	# Query data
	#
	# Salesforce returns bulk data in the form of CSV-encoded text, but it's not
	# quite ready to write to disk, since we need to change the dialect to match our
	# input sample, insert comma delimiters back into AnnualRevenue, and prevent
	# duplicate header rows at the top of each batch.
	#
	# To handle this, we'll query the data in batches of 500, then format and
	# write the resulting data one row at a time.
	fields = ['Id',
			  'Name',
			  'BillingStreet',
			  'BillingCity',
			  'BillingCountry',
			  'BillingPostalCode',
			  'BillingState',
			  'ShippingStreet',
			  'ShippingCity',
			  'ShippingCountry',
			  'ShippingPostalCode',
			  'ShippingState',
			  'NumberOfEmployees',
			  'Phone',
			  'AnnualRevenue']
	query = (f"SELECT {','.join(fields)} FROM Account")

	result = session.bulk2.Account.query(query, max_records=500)
	# queries will happen one batch at a time as we read out the result
	with open(outfile, 'w+', newline='') as f:
		writer = csv.DictWriter(f, fieldnames=fields, quoting=csv.QUOTE_MINIMAL)
		writer.writeheader()
		# Each job represents a batch of up to 500 records
		for i, job in enumerate(result):
			print(f"Downloading batch {i+1}...")
			reader = csv.DictReader(job.splitlines())
			for row in reader:
				try:
					row['AnnualRevenue'] = (f"{(float)(row['AnnualRevenue']):,}")
				except ValueError as e:
					print(f"Warning: AnnualRevenue value {row['AnnualRevenue']} couldn't be converted to a float")
				writer.writerow(row)
	print(f"{outfile} saved successfully!")

if __name__ == "__main__":
	main()

