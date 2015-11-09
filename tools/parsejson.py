################################################################################

import json
import codecs
################################################################################

__all__ = []


def export(obj):
    __all__.append(obj.__name__)
    return obj


################################################################################
# parse_json() parses an json file and returns the parsed elements in dictionary.
#
@export
def parse_json(filename):
    data = {}
    try:
        with codecs.open(filename, 'r', 'utf-8-sig') as data_file:
            data = json.load(data_file)
    except IOError:
        pass
    except ValueError as e:
        print e
        pass
    return data


if __name__ == '__main__':
    pass
