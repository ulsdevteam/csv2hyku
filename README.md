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

There is a `bulkrax2yaml.py` which will take a Bulkrax Field Mappings JSON file (superadmin -> Accounts -> Edit Account), and will convert it to a YAML configuration file for `csv2hyku.py`.  Manual edits will be needed to add desired `transform` options, such as (notably) "file".  Bulkrax also allows for flexible separators, such as `(?-mix:\s*[;|]\s*)`, which will need to be simplified to just the single separator you are actually using in the data.

A sample conversion is provided as "bulkrax-mapping.yaml", from the "bulkrax.json" file downloaded from hykucommons.org.  This tool reads from `STDIN` and writes to `STDOUT`.

For compatibility with bulkrax CSVs, you'll almost certainly want to use case insensitive header matching.

#### Other notes

* The XML will be built in order of the column names found in the CSV header
* Empty values in the CSV will not create empty XML elements
* There is a command line option if you want the CSV headers to be case insensitive

## Configuration YAML

The Configuration YAML includes keys for:
* sword_baseurl: What is the base URL to your Hyku tenant?
* collection: What is the admin set into which we are depositing?
* api_key: What is the API key for your deposit user?
* work_type: What is the Hyku work model to submit as an HTTP header?

See `hyku-sword.yml.sample` for an example.

## CSV value rewriting

If your CSV has values which do not directly map to input values for SWORD, there is a `transform` operation available called "rewrite" which will read a YAML file to replace input values with output values.  This is useful, for example, if processing a Bulkrax CSV where the `parents` field references bulkrax collection identifiers rather than Hyku identifiers.  The "rewrite" operation consists of the string-literal "rewrite:" followed by path to the YAML key-value file.  The path will be interpreted as abolute, relative to the working directory, or relative to the YAML mapping file, in that order.  The rewrite key-value pairs need not be comprehensive; an unrecognized value will be passed through untouched.

### Example
YAML mapping:
```
parents:
  name: member_of_collection_ids
  separator: "|"
  transform: "rewrite:collections.yaml"
```

`collections.yaml`
```
fruit_collection: f5a892b4-7ec7-4090-8f43-7a491d5d5484
vegetable_collection: 7e6f9ba6-dc96-4625-9d7e-46e893a8b164
grain_collection: 91eccf5b-5d44-4e1f-9ae3-c04fb29887a5
```

CSV `parents` column:
```
fruit_colleciton|vegetable_collections|seed_collection
```

XML output:
```
<member_of_collection_ids>f5a892b4-7ec7-4090-8f43-7a491d5d5484</member_of_collection_ids>
<member_of_collection_ids>7e6f9ba6-dc96-4625-9d7e-46e893a8b164</member_of_collection_ids>
<member_of_collection_ids>seed_collection</member_of_collection_ids>
```

### creating the YAML rewrite file for collections

If you have the bulkrax file used to ingest the new collections, a script is provided to read the collection name and bulkrax identifier column, look up the collection list in SWORD, and match the collections base on names.  This assumes unique collection names, and assumes that your bulkrax collections CSV has the identifer in `source_identifier` and the name in `title`.  It will also require a SWORD configuration YAML as input.  The rewrite YAML will be written to STDOUT; warnings about duplicate titles and unrecognized collections will be written to STDERR.

```
python3 rewritecollections.py --config=sword-credentials.yml --csv=collections.csv > collections.yml
```


## Usage

The process has two steps:
* `csv2hyku.py` takes in a CSV file and creates a directory of .zip files in SimpleZip format.
* `swordsend.py` takes in a directory of .zip files and POSTs them to the SWORD endpoint

`python3 csv2hyku.py -h` and `python3 swordsend.py -h` for inline help

### Quickstart

* Copy the `generic-mapping.yml` or `bulkrax-mapping.yml` to your own `mapping.yml` file
* Align the keys of the `mapping.yml` file to your CSV
* Copy the `hyku-sword.yml.sample` to your own `sword-config.yml` file
* Edit the `sword-config.yml` file values to match your Hyku tenant
* Run `csv2hyku.py`, specifying the `mapping.yml` file, your CSV, and the output directory to write the zip files
* Run `swordsend.py`, specifying the `sword-config.yml` file and the directory where you wrote the zip files

### Example

In this example, you have the `csv2hyku` application under your home directory, and in `/data/bulkrax` you have a bulkrax CSV and deposit files refernced by relative paths.  Set up the configuration for mapping and Hyku access, then switch to the bulkrax directory (so the relative paths work), and reference the applications and configs in the arguments.

```
cp bulkrax-mapping.yml columns.yml
vi columns.yml
cp hyku-sword.yml.sample secrets.yml
vi secrets.yml
cd /data/bulkrax
python3 ~/csv2hyku/csv2hyku.py --input=generics.csv --output=zipfiles --mapping=~/csv2hyku/columns.yml --ignore-case
python3 ~/csv2hyku/swordsend.py --input=zipfiles --config=~csv2hyku/secrets.yml
```

## License

Copyright (c) University Library System, University of Pittsburgh

Released under the MIT license
