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

### Vars ###

bulk_data = []

### Implementation ###

def getCreds():
	config = configparser.ConfigParser()
	config.read(CREDENTIALS_FILE)
	return (config['sandbox']['Endpoint'], config['sandbox']['Token'])

def main():
	# Ensure the user provided the input CSV file name as an argument
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

	# Open and process the CSV file 
	#
	# Using the synchronous row update API is extremely slow for >1000 records,
	# so we'll Bulk2 API as documented here: 
	# https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/bulk_api_2_0_ingest.htm
	print(f"Reading data from {datafile}")
	with open(datafile, 'r', newline='') as f:
		reader = csv.DictReader(f)
		# Field names in the sample CSV match the API field names, so we don't need to remap them
		for row in reader:
			# Do some basic data integrity checking
			if None in row.keys():
				print(f"Warning: row {reader.line_num} has extra fields. Skipping it. {row}")
				continue
			if None in row.values():
				print(f"Warning: row {reader.line_num} has too few fields. Skipping it. {row}")
				continue
			# Normalize currency formatting
			row['AnnualRevenue'] = row['AnnualRevenue'].replace(',', '')
			bulk_data.append(row)

	# Now we have all our data formatted the way SalesForce needs it in a dict.
	# Let's commit it.

	# Connect to SalesForce/TrailHead
	# Note that the security token needs to be passed in as 'session_id',
	# not 'security_token', which is only used for JWT tokens
	session = simple_salesforce.Salesforce(instance=inst, session_id=token)
	print("Connected to SalesForce. Starting bulk import")
	try:
		result = session.bulk2.Account.upsert(records=bulk_data, batch_size=500)
		for i, job in enumerate(result):
			print(f"Batch {i+1} of {len(result)}:")
			totalRecs = result[i]['numberRecordsProcessed']
			failedRecs = result[i]['numberRecordsFailed']
			print(f"\t{totalRecs - failedRecs} out of {totalRecs} records processed successfully")
			if failedRecs > 0:
				fail_data = session.bulk2.Account.get_failed_records(job['job_id'])
				print("Failure messages:")
				print(fail_data)
	except simple_salesforce.exceptions.SalesforceMalformedRequest as e:
		print(f"Exception with bulk import")

if __name__ == "__main__":
	main()

