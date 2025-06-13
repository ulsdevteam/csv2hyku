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
  * '': trim leading and trailing whitespace from the value

### Examples:

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

YAML snippet:
```
Filenames:
  name: file
  separator: '|'
  transform: 'file'
```

For a CSV column with the first row header of "Filenames", and the cell value of "Disseration.pdf|supplemental/table.csv|supplemental/references.txt", the XML metadata will have no change, but three files will be added to the SWORD deposit, based on their relative paths to the current working directory.

## Configuration YAML

TODO

## Usage

`csv2hyku -h` for inline help


