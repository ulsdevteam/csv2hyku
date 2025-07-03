import csv

def check_utf8_sign(filename):
    """
    Check if there is a byte-order-marker on the UTF-8 file

    Args
      filename (str): the path and name of the file to check

    Return
      str: the file encoding signature
    """
    file_encoding = 'utf-8'
    f = open(filename, 'r', newline='', encoding=file_encoding)
    first_line = f.read()
    if first_line.startswith('\ufeff'):
        file_encoding = 'utf-8-sig'
    f.close()
    return file_encoding

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


