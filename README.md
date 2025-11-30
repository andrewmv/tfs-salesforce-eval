# TFS SalesForce Trailhead Assessment Evaluation

## Objectives

* Ingest CSV data into workspace as account records
* Retrive account records and repopulate back into new CSV

## Requirements

* Python 3.9+
* [simple-salesforce](https://pypi.org/project/simple-salesforce/)

The only module we use from outside of the standard Python distribution is 
[simple-salesforce](https://pypi.org/project/simple-salesforce/), which
provides a simple wrapper around SalesForce's publically documented REST APIs.

## Installation

Clone repo

	git clone https://github.com/andrewmv/tfs-salesforce-eval.git
	cd tfs-salesforce-eval

Create and activate a Python3 virtual environment

	python3 -m venv tfs-eval-venv
	source ./tfs-eval/venv/bin/activate

Install dependencies

	pip install -r requirements.txt

## Usage

### Authentication

All of the tools in this project will read endpoint and authentication data from the `.creds` file.

Use the [SalesForce CLI](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/quickstart_oauth.htm) to get a session authentiation token

	sf org login web --instance-url https://<playground name>.trailblaze.my.salesforce.com

Complete OAuth steps presented in browser, then:

	sf org display --target-org <org name>

Create a file in the project directory called `.creds` with the following contents:

	[sandbox]
	Endpoint = <playground name>.trailblaze.my.salesforce.com
	Token = <token from previous step>

### Importing data to SalesForce/Trailhead

Usage:

	./import.py sample_data.csv

### Exporting data from SalesForce/Trailhead

Usage:

	./export.py output.csv

### Methodology

Both of these example utilize SalesForce's Bulk2.0 API, which is significantly faster than the
per-record API for uploading/downloading large numbrers of a single type of recrod.

### Additional Notes

The provided sample data file (consisting of 5000 records) won't fit within a free TrailHead sandbox, so I've truncated the sample data set to 2000 records.

The `deleteAccount.py` utility can be used to purge all the sample data from the sandbox to simplify re-running the assessment.