# Hyku SWORD CSV converter

Given a CSV file with metadata, and optional works files to deposit, create SWORD deposits for Hyku.

## Requirements

* Python 3
* dependencies via requirements.txt
* a YAML mapping file describing the CSV
* A CSV with one row per Work, columns with the metadata, encoded in UTF-8
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

#### `name` values can be repeated

YAML snippet:
```
Keywords:
  name: keyword
  separator: ','
  transform: 'strip'
keyword 1:
  name: keyword
keyword 2:
  name: keyword
keyword 3:
  name: keyword
```

If the prior example also had column headers of "keyword 1" and "keyword 2", with respective values of "Peas", and "Carrots", the XML metadta snippet will be:
```
  <keyword>Broccoli</keyword>
  <keyword>Cauliflower</keyword>
  <keyword>Collard Greens</keyword>
  <keyword>Peas</keyword>
  <keyword>Carrots</keyword>
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

#### A complete mapping to bulkrax

There is a `bulkrax2yaml.py` which will take a Bulkrax Field Mappings JSON file (superadmin -> Accounts -> Edit Account), and will convert it to a YAML configuration file for `csv2hyku.py`.  Manual edits will be needed to add desired `transform` options, such as (notably) "file".

A sample conversion is provided as "bulkrax-mapping.yaml", from the "bulkrax.json" file downloaded from hykucommons.org.  This tool reads from `STDIN` and writes to `STDOUT`.

For compatibility with bulkrax CSVs, you'll almost certainly want to use case insensitive header matching.

#### Other notes

* The XML will be built in order of the column names found in the CSV header
* Empty values in the CSV will not create empty XML elements
* There is a command line option if you want the CSV headers to be case insensitive

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
