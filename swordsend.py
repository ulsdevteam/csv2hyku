import os
import yaml
import requests
import logging
import argparse

def main():
    """
    Given CLI args with an input directory with zip files, and a config file of authentication info for the Hyku endpoint
    Iterate across each zip file, uploading it to the SWORD endpoint as a new Work

    Report errors to STDERR, and info if the loglevel is sufficiently low
    """
    # Command line arguments
    parser = argparse.ArgumentParser(
        prog='swordsend',
        description='Process a directory as Hyku SWORD deposits')
    parser.add_argument('--config', required=True, type=str, help='The YAML configuation file')
    parser.add_argument('--input', required=True, type=str, help='The input directory')
    parser.add_argument('--loglevel', help='The log level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='ERROR')
    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(level=getattr(logging, args.loglevel), format='%(levelname)s: %(message)s')

    # Read configuration file
    with open(args.config) as yf:
        config = yaml.safe_load(yf)
    endpoint = config['sword_baseurl'] + '/collections/' + config['collection'] + '/works/'

    # read the input directory, the YAML config, and deposit to the SWORD endpoint
    for filename in os.listdir(args.input):
        if filename.endswith('.zip'):
            filepath = os.path.join(args.input, filename)
            with open(filepath, 'rb') as zf:
                headers = {
                    'Content-Disposition': f'attachment; filename={filename}',
                    'Content-type': 'application/zip',
                    'Packaging': 'http://purl.org/net/sword/package/SimpleZip',
                    'Hyrax-Work-Model': config['work_type'],
                    'Api-key': config['api_key']
                }
                response = requests.post(endpoint, headers=headers, data=zf)
                if response.status_code == 201:
                    logging.info(f'Submitted {filename} with {response.status_code} response')
                else:
                    logging.error(f'Failure for {filename} with {response.status_code} response')
                    logging.info(f'{response.content}')
    exit()

if __name__ == "__main__":
    main()
