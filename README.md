# Hyku SWORD CSV converter

Given a CSV file with metadata, and optional works files to deposit, create SWORD deposits for Hyku.

## Requirements

* Python 3
* dependencies via requirements.txt
* a YAML mapping file describing the CSV
* A CSV with one row per Work, columns with the metadata
* a configuration YAML describing the Hyku 6+ tenant and credentials

## YAML mapping

The YAML mapping is in the form of a key representing the CSV column header, mapped to subkeys:
* name: the SWORD element name
* separator: a character on which to split the cell value, for multiples
* transform: a processer name used to process the cell values
  * 'file': treat this value as a filename, copy the file to the deposit
  * 'strip': trim leading and trailing whitespace from the value

### Examples:

#### A simple field

YAML snippet:
```
Abstract:
  name: abstract
```

For a CSV column with the first row header of "Abstract", and the cell value of:
"Hyku SWORD CSV

A tool to get CSVs into Hyku via SWORD"
the XML metadta snippet will be:
```
  <abstract>Hyku SWORD CSV

A tool to get CSVs into Hyku via SWORD</abstract>
```

#### A field with multiple values, and a transformation

YAML snippet:
```
Keywords:
  name: keyword
  separator: ','
  transform: 'strip'
```

For a CSV column with the first row header of "Keywords", and the cell value of "Broccoli, Cauliflower, Collard Greens", the XML metadta snippet will be:
```
  <keyword>Broccoli</keyword>
  <keyword>Cauliflower</keyword>
  <keyword>Collard Greens</keyword>
```

#### The work files field

YAML snippet:
```
Filenames:
  name: None
  separator: '|'
  transform: 'file'
```

For a CSV column with the first row header of "Filenames", and the cell value of "Disseration.pdf|supplemental/table.csv|supplemental/references.txt", the XML metadata will have no change, but three files will be added to the SWORD deposit, based on their relative paths to the current working directory.  A value for the `name` subkey is required, but ignored.

## Configuration YAML

The Configuration YAML include keys for:
* sword_baseurl: What is the base URL to your Hyku tenant?
* api_key: What is the API key for your deposit user?
* work_type: What is the Hyku work model to submit as an HTTP header?

## Usage

`python3 csv2hyku.py -h` for inline help

## License

Copyright (c) University Library System, University of Pittsburgh

Released under the MIT license
