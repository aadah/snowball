import json
import os


def to_unicode(text, encoding='utf-8'):
    return text.decode(encoding)


def to_string(text, encoding='utf-8'):
    return text.encode('utf-8')


def to_lowercase(string):
    return string.lower()


def write_line(f, obj):
    f.write("%r\n" % obj)


def write_string(f, string):
    f.write(to_string(string) + "\n")


def load_json(path):
    j = None

    with open(path) as f:
        j = json.load(f)

    return j


def save_json(j, f):
    json.dump(j, f, sort_keys=True, indent=4)


def list_files(path):
    return [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]


def list_directories(path):
    return [os.path.join(path, d) for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]


def list_files_up_to(path, depth):
    if depth == 0: return []

    files = list_files(path)
    dirs = list_directories(path)

    for d in dirs:
        files.extend(list_files_up_to(d, depth-1))

    return files


def parse_seed_file(path):
    f = open(path)
    rel = f.readline().strip()
    tags = f.readline().strip().split()
    subj_tag = tags[0]
    obj_tag = tags[1]
    tup_strings = f.readlines()
    pairs = []
    seed_dict = {}

    for string in tup_strings:
        tokens = string.strip().split()
        subj = tokens[0]
        obj = tokens[1]
        pairs.append((to_unicode(subj),
                      to_unicode(obj)))

    seed_dict[u'rel'] = to_unicode(rel)
    seed_dict[u'subj_tag'] = to_unicode(subj_tag)
    seed_dict[u'obj_tag'] = to_unicode(obj_tag)
    seed_dict[u'pairs'] = pairs

    f.close()

    return seed_dict
