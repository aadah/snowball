import argparse

from utils import io
from elastic import es
from config import config


def main(args):
    if args.delete:
        ans = raw_input("Are you sure (y/[n])? ")
        if ans == 'y':
            print es.delete_index(args.index)
        else:
            print "Aborted."
        return

    page_mapping = io.load_json(config.ELASTICSEARCH_PAGE_MAPPING_FILE)
    sentence_mapping = io.load_json(config.ELASTICSEARCH_SENTENCE_MAPPING_FILE)
    print es.create_index(args.index)
    print es.put_page_mapping(page_mapping)
    print es.put_sentence_mapping(sentence_mapping)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()

    argparser.add_argument('-d', '--delete',
                           action='store_true',
                           help='delete the index')

    argparser.add_argument('-i', '--index',
                           default=config.ELASTICSEARCH_INDEX,
                           help='index name to create/delete')

    args = argparser.parse_args()

    main(args)
