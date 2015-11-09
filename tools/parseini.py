################################################################################

__all__ = []


def export(obj):
    __all__.append(obj.__name__)
    return obj


################################################################################
# parse_ini_text() parses name-value pairs and returns the parsed elements in dictionary.
#
@export
def parse_ini_text(lines):
    ini = {}
    for line in lines:
        if line.find('=') == -1:
            continue
        key, value = line.split('=', 1)
        value = value.strip()
        ini[key] = value
    return ini


################################################################################
# parse_ini() parses an ini file and returns the parsed elements in dictionary.
#
@export
def parse_ini(filename):
    ini = {}
    if filename is not None:
        fp = open(filename, 'r')
        ini = parse_ini_text(fp.readlines())
        fp.close()
    return ini


if __name__ == '__main__':
    pass
