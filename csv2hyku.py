import csv
import yaml
import os
import xml.etree.ElementTree as ET
import logging
import argparse
import shutil

class IgnoreCaseDictReader(csv.DictReader):
    """
    Override DictReader to ignore the case of column headers
    """

    @property
    def fieldnames(self):
        """
        fieldnames property is lowecase of each DictReader fieldname
        """
        return [field.lower() for field in csv.DictReader.fieldnames.fget(self)]
    def next(self):
        """
        next() returns next, but lowecase
        """
        return IgnoreCaseDict(csv.DictReader.next(self))

class IgnoreCaseDict(dict):
    """
    Override dict to ignore the case of key
    """

    def __getItem__(self, key):
        """
        getItem returns getitem, but lowercase
        """
        return dict.__getitem__(self, key.lower())

def write_element(parent, element_name, value, transform, target_dir):
    """
    Add a new element to the tree, with optional transformation

    Args:
      parent (xml.etree.ElementTree.Element): the node to which to add the new element
      element_name (str): the name of the new element
      value (str): the value of the new element
      transform (str): a transformation to apply to the element value
      target_dir (str): a working context directory, if file ops are needed for the transform

    Return:
      None

    Side effects:
      May modify the parent
      May write to the target_dir
      May output logging
    """

    # Special transformation: treat the value as a filename and copy it to the target_dir
    # No element will be created
    if transform == 'file':
        try:
            if value:
                shutil.copy(value, os.path.join(target_dir, os.path.basename(value)))
        except FileNotFoundError as e:
            logging.error(f"File not found: {value}")
        return
    
    # General transformations
    if transform == 'strip':
        value = value.strip()
    elif transform != None:
        logging.warning(f"Unknown transform {transform}")

    # Don't write empty elements
    if !value:
        return

    # Append the new element to the parent with the new value
    element = ET.SubElement(parent, element_name)
    element.text = value

def csv_to_xml(csv_file, yaml_file, output_dir, ignore_case=False):
    """
    Transform a CSV file row by row to a Hyku SWORD deposit (XML + files)

    Args:
      csv_file (str): filename for the CSV input
      yaml_file (str): filename for the YAML configuration
      output_dir (str): where to write the resulting XML + files
      ignore_case (bool): Will use case insensitive CSV headers

    Return:
      None

    Side effects:
      The output_dir will have multiple subdirectories created, one per CSV row
      May output logging

    The CSV must have a header row.
    The YAML will be tokens mapping the header row names to:
      name: the XML element name
      separator: a character to use to split mulitple values in a single CSV cell
      transform: an operation to perform on the individual values (see: write_element)
    """

    # Load YAML configuration
    with open(yaml_file, 'r') as yf:
        config = yaml.safe_load(yf)

    # Ensure output directory exists
    if os.path.isdir(output_dir):
        logging.info(f"The output directory already exists: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)

    # Read CSV file
    with open(csv_file, 'r', newline='', encoding='utf-8') as cf:
        if ignore_case:
            reader = IgnoreCaseDictReader(cf)
        else:
            reader = csv.DictReader(cf)
        headers = reader.fieldnames

        for row_number, row in enumerate(reader, start=1):
            logging.debug(f"Begin CSV row {row_number}")

            # Ensure output subdirectory exists
            row_output_dir = os.path.join(output_dir, f"row_{row_number}")
            if os.path.isdir(row_output_dir) and len(os.listdir(row_output_dir)) != 0:
                logging.warning(f"The row directory exists and was not empty: {row_output_dir}")
            os.makedirs(row_output_dir, exist_ok=True)

            # Create XML root element
            root = ET.Element('metadata')

            # each column in the row will be mapped to an element via the column header
            for header, value in row.items():
                # the YAML config will tell us how to process this column/value
                if header in config:
                    xml_element_name = config[header]['name']
                    separator = config[header].get('separator')
                    transform = config[header].get('transform')

                    if separator and separator in value:
                        values = value.split(separator)
                        for val in values:
                            write_element(root, xml_element_name, val, transform, row_output_dir)
                    else:
                        write_element(root, xml_element_name, value, transform, row_output_dir)
                # Ignore headers not in config

            # Check for headers in YAML config that are not in CSV
            for yaml_header in config:
                if yaml_header not in headers:
                    logging.debug(f"Mapping for header '{yaml_header}' found in YAML configuration but not in CSV.")

            # Write XML to file
            tree = ET.ElementTree(root)
            xml_filename = os.path.join(row_output_dir, f"metadata.xml")
            tree.write(xml_filename, encoding='utf-8', xml_declaration=True)

def main():
    # Command line arguments
    parser = argparse.ArgumentParser(
        prog='csv2hyku',
        description='Transform a CSV into Hyku SWORD deposit files')
    parser.add_argument('--mapping', required=True, type=str, help='The YAML configuation file')
    parser.add_argument('--input', required=True, type=str, help='The input CSV file')
    parser.add_argument('--output', required=True, type=str, help='The output directory')
    parser.add_argument('--ignore-case', action='store_true')
    parser.add_argument('--loglevel', help='The log level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='ERROR')
    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(level=getattr(logging, args.loglevel), format='%(levelname)s: %(message)s')

    # read the CSV input, the YAML config, and write to the output directory
    csv_to_xml(args.input, args.mapping, args.output, args.ignore_case)
    exit() 

if __name__ == "__main__":
    main()
