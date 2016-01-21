from classes import *
from utils import io
from config import config


def read_tuples():
    pairs = []
    f = open(config.SNOWBALL_TUPLES_FILE)
    strings = f.readlines()
    f.close()

    for line in strings:
        o = eval(io.to_unicode(line))
        
        if type(o) is not str:
            pair = u"%s\t%s" % (o.subj, o.obj)
            pairs.append(io.to_string(pair))

    return pairs


def main():
    pairs = read_tuples()

    for pair in pairs:
        print pair


if __name__ == '__main__':
    main()
