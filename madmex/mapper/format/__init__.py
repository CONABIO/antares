from madmex import find_in_dir
from madmex import load_class

FORMATS_PACKAGE = 'madmex.mapper.format'
def find_formats():

    return find_in_dir(__path__[0],'')

def find_specifications(format_type):
    try:
        specifications = load_class(FORMATS_PACKAGE, format_type).SPECIFICATIONS
    except AttributeError:
            specifications = None
    return specifications
    

