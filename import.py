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

def main():
	# Ensure the user provided the CSV file name as an argument
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

	# Open CSV file - we'll keep the filehandle open and process records as we read them.
	# This will scale better to larger data dumps.
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
			# This row looks good, import it
			print(f"Importing {row['Name']}")
			try:
				session.Account.create(row)
			except simple_salesforce.exceptions.SalesforceMalformedRequest as e:
				print(f"Exception importing row: {row}")
				print(e)
				break

if __name__ == "__main__":
	main()

