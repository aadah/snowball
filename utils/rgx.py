import re

from config import config


start_tag_rgx = re.compile(config.WIKIPEDIA_START_TAG_RGX)
end_tag_rgx = re.compile(config.WIKIPEDIA_END_TAG_RGX)
token_rgx = re.compile("^<(.*)>(.*)<.*>$")


def replace_digits(string):
    string = string.replace("0", " zero ")
    string = string.replace("1", " one ")
    string = string.replace("2", " two ")
    string = string.replace("3", " three ")
    string = string.replace("4", " four ")
    string = string.replace("5", " five ")
    string = string.replace("6", " six ")
    string = string.replace("7", " seven ")
    string = string.replace("8", " eight ")
    string = string.replace("9", " nine ")

    return string


def nonalphanumeric_to_space(string):
    string = re.sub(r'\W+', ' ', string)

    return string


def page_start(string):
    if start_tag_rgx.match(string):
        return True

    return False


def page_end(string):
    if end_tag_rgx.match(string):
        return True

    return False


def create_template_rgx(tag):
    return re.compile("^<%s>.*</%s>$" % (tag, tag))


def extract_string(t1):
    m = token_rgx.match(t1)
    return m.groups()[1]


def extract_entity(t1):
    m = token_rgx.match(t1)
    return m.groups()[0]


#def match_indices(pattern, string):
#    return [(m.start(), m.end()) for m in re.finditer(pattern, string)]


#def not_overlapping(p1, p2):
#    return p1[1] <= p2[0] or p1[0] >= p2[1]
