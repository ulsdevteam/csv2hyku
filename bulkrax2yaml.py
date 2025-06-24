import json
import yaml
import argparse
import sys

def main():
    # command line arguments (none)
    parser = argparse.ArgumentParser(
        prog='bulkrax2yaml',
        description='Transform a bulkrax field mapping JSON to a csv2hyku YAML')
    args = parser.parse_args()

    # this dictionary will be expressed as YAML
    mapping = {}

    # read STDIN as JSON
    bulkrax = json.load(sys.stdin)
    # fields are Hyku data elements
    root_element = 'Bulkrax::BagitParser'
    for field in bulkrax[root_element]:
        # aliases are the possible column headers to name this element in the Bulkrax CSV
        for alias in bulkrax[root_element][field]['from']:
            # split maps directly to our separator
            if bulkrax[root_element][field].get('split'):
                mapping[alias] = { "name": field, "separator": bulkrax[root_element][field].get('split') }
            else:
                mapping[alias] = { "name": field }
    # print with block indentation
    print(yaml.dump(mapping, default_flow_style=False))
    exit() 

if __name__ == "__main__":
    main()
