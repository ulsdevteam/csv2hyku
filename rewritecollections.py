import yaml
import requests
import logging
import argparse
import xml.etree.ElementTree as ET
import utilityfunctions
from utilityfunctions import *

def main():
    """
    Given CLI args with an input bulkrax collection CSV, and a config file of authentication info for the Hyku endpoint
    Download the SWORD service document to enumerate the collections, then find the matching collection by name in the CSV
    Write out a YAML mapping of bulkrax identifier to the collection GUID

    Report errors to STDERR, and info if the loglevel is sufficiently low
    """
    # Command line arguments
    parser = argparse.ArgumentParser(
        prog='swordsend',
        description='Process a directory as Hyku SWORD deposits')
    parser.add_argument('--config', required=True, type=str, help='The YAML configuation file')
    parser.add_argument('--csv', required=True, type=str, help='The input csv')
    parser.add_argument('--loglevel', help='The log level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='ERROR')
    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(level=getattr(logging, args.loglevel), format='%(levelname)s: %(message)s')

    # Read configuration file
    with open(args.config) as yf:
        config = yaml.safe_load(yf)
    endpoint = config['sword_baseurl'] + '/service_document'

    # read the CSV, index it by title in "csv"
    csv = {}
    file_encoding = utilityfunctions.check_utf8_sign(args.csv)
    with open(args.csv, 'r', newline='', encoding=file_encoding) as cf:
        reader = IgnoreCaseDictReader(cf)
        for row_number, row in enumerate(reader, start=1):
            logging.debug(f"Begin CSV row {row_number}")
            if row['title']:
                if csv.get(row['title']):
                    logging.error(f'The title {row["title"]} is duplicated in the bulkrax CSV')
                elif row.get('source_identifier'):
                    csv[row['title']] = row['source_identifier']
                else:
                    logging.error(f'The title {row["title"]} does not have an associated identifier')

    # read the service document, create an output mapping the bulkrax identifier to the collection GUID
    output = {}
    headers = {
        'Content-type': 'application/xml',
        'Api-key': config['api_key']
    }
    response = requests.get(endpoint, headers=headers)
    if response.status_code != 200:
        logging.error(f'Service Document failure with {response.status_code} response')
        logging.info(f'{response.content}')
        exit(1)
    doc = ET.fromstring(response.content)
    for collection in doc.findall(".//{http://www.w3.org/2007/app}collection"):
        # the collection has a title which will be the matchpoint
        name = collection.find('{http://www.w3.org/2005/Atom}title')
        # the collection has an href which ends with the GUID
        url = collection.attrib['href']
        uuid = url.replace(config['sword_baseurl'] + '/collections/', '')
        logging.debug(f'Name "{name.text}" is {uuid}')
        # map from the CSV (bulkrax source id) to the GUID
        if csv.get(name.text):
            output[csv[name.text]] = uuid
        else:
            logging.error(f'No bulkrax CSV entry found for {name.text}')

    print(yaml.dump(output, default_flow_style=False))

    exit()

if __name__ == "__main__":
    main()
