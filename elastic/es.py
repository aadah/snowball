import math
from elasticsearch import Elasticsearch

from config import config


client = Elasticsearch([{'host': config.ELASTICSEARCH_HOST,
                         'port': config.ELASTICSEARCH_PORT}])


def create_index(index):
    return client.indices.create(index=index, ignore=400)


def delete_index(index):
    return client.indices.delete(index=index, ignore=[400, 404])

####################################################################################

def put_page_mapping(mapping, index=config.ELASTICSEARCH_INDEX, doc_type=config.ELASTICSEARCH_PAGE_TYPE):
    return client.indices.put_mapping(
        doc_type=doc_type,
        body=mapping,
        index=index)


def put_sentence_mapping(mapping, index=config.ELASTICSEARCH_INDEX, doc_type=config.ELASTICSEARCH_SENTENCE_TYPE):
    return client.indices.put_mapping(
        doc_type=doc_type,
        body=mapping,
        index=index)


def put_raw_sentence_mapping(mapping, index=config.ELASTICSEARCH_INDEX, doc_type=config.ELASTICSEARCH_RAW_SENTENCE_TYPE):
    return client.indices.put_mapping(
        doc_type=doc_type,
        body=mapping,
        index=index)


def get_mapping(doc_type, index=config.ELASTICSEARCH_INDEX):
    return client.get_mapping(
        index=index,
        doc_type=doc_type)

####################################################################################

def page_exists(pageId, index=config.ELASTICSEARCH_INDEX, doc_type=config.ELASTICSEARCH_PAGE_TYPE):
    return client.exists(index=index,
                         doc_type=doc_type,
                         id=pageId)

####################################################################################

def index_page(page, index=config.ELASTICSEARCH_INDEX, doc_type=config.ELASTICSEARCH_PAGE_TYPE):
    return client.index(
        index=index,
        doc_type=doc_type,
        body=page,
        id=str(page['id']))


def index_sentence(sentence, index=config.ELASTICSEARCH_INDEX, doc_type=config.ELASTICSEARCH_SENTENCE_TYPE):
    return client.index(
        index=index,
        doc_type=doc_type,
        body=sentence,
        id="%d_%d" % (sentence['id'], sentence['index']))


def index_raw_sentence(sentence, index=config.ELASTICSEARCH_INDEX, doc_type=config.ELASTICSEARCH_RAW_SENTENCE_TYPE):
    return client.index(
        index=index,
        doc_type=doc_type,
        body=sentence,
        id="%d_%d" % (sentence['id'], sentence['index']))

####################################################################################

def count_pages(index=config.ELASTICSEARCH_INDEX, doc_type=config.ELASTICSEARCH_PAGE_TYPE):
    return client.count(index=index,
                        doc_type=doc_type)['count']


def count_sentences(index=config.ELASTICSEARCH_INDEX, doc_type=config.ELASTICSEARCH_SENTENCE_TYPE):
    return client.count(index=index,
                        doc_type=doc_type)['count']


def count_raw_sentences(index=config.ELASTICSEARCH_INDEX, doc_type=config.ELASTICSEARCH_RAW_SENTENCE_TYPE):
    return client.count(index=index,
                        doc_type=doc_type)['count']


def count_sentences_containing(tup, index=config.ELASTICSEARCH_INDEX, doc_type=config.ELASTICSEARCH_SENTENCE_TYPE):
    body = {
        "query": {
            "filtered": {
                "filter": {
                    "and": [
                        {"term": {"tagged_tokens": tup.subj_string()}},
                        {"term": {"tagged_tokens": tup.obj_string()}}
                    ]
                }
            }
        }
    }

    return client.count(index=index,
                        doc_type=doc_type,
                        body=body)['count']


def count_sentences_with_tags(tag_one, tag_two, index=config.ELASTICSEARCH_INDEX, doc_type=config.ELASTICSEARCH_SENTENCE_TYPE):
    body = {
        "query": {
            "filtered": {
                "filter": {
                    "and": [
                        {"term": {"entities": tag_one}},
                        {"term": {"entities": tag_two}}
                    ]
                }
            }
        }
    }

    return client.count(index=index,
                        doc_type=doc_type,
                        body=body)['count']


def count_sentences_with_token(token, index=config.ELASTICSEARCH_INDEX, doc_type=config.ELASTICSEARCH_SENTENCE_TYPE):
    body = {
        "query": {
            "filtered": {
                "filter": {
                    "regexp": {"tokens": "(.+_)?%s(_.+)?" % token}
                }
            }
        }
    }

    return client.count(index=index,
                        doc_type=doc_type,
                        body=body)['count']

####################################################################################

def get_sentences_containing(tup, from_offset=0, size=config.ELASTICSEARCH_RESULTS_SIZE, index=config.ELASTICSEARCH_INDEX, doc_type=config.ELASTICSEARCH_SENTENCE_TYPE):
    body = {
        "from": from_offset,
        "query": {
            "filtered": {
                "filter": {
                    "and": [
                        {"term": {"tagged_tokens": tup.subj_string()}},
                        {"term": {"tagged_tokens": tup.obj_string()}}
                    ]
                }
            }
        }
    }

    return client.search(index=index,
                         doc_type=doc_type,
                         body=body,
                         size=size)['hits']['hits']


def get_raw_sentences_with_substrings_in_page(page_id, substring1, substring2, from_offset=0, size=config.ELASTICSEARCH_RESULTS_SIZE, index=config.ELASTICSEARCH_INDEX, doc_type=config.ELASTICSEARCH_RAW_SENTENCE_TYPE):
    body = {
        "from": from_offset,
        "query": {
            "filtered": {
                "filter": {
                    "and": [
                        {"term": {"id": page_id}},
                        {"regexp": {"text": ".*%s.*" % substring1}},
                        {"regexp": {"text": ".*%s.*" % substring2}}
                    ]
                }
            }
        }
    }

    return client.search(index=index,
                         doc_type=doc_type,
                         body=body,
                         size=size)['hits']['hits']


def get_raw_sentences_with_substring(substring, from_offset=0, size=config.ELASTICSEARCH_RESULTS_SIZE, index=config.ELASTICSEARCH_INDEX, doc_type=config.ELASTICSEARCH_RAW_SENTENCE_TYPE):
    body = {
        "from": from_offset,
        "query": {
            "filtered": {
                "filter": {
                    "regexp": {"text": ".*%s.*" % substring}
                }
            }
        }
    }

    return client.search(index=index,
                         doc_type=doc_type,
                         body=body,
                         size=size)['hits']['hits']


def get_sentences_with_tags(tag_one, tag_two, from_offset=0, size=config.ELASTICSEARCH_RESULTS_SIZE, index=config.ELASTICSEARCH_INDEX, doc_type=config.ELASTICSEARCH_SENTENCE_TYPE):
    body = {
        "from": from_offset,
        "query": {
            "filtered": {
                "filter": {
                    "and": [
                        {"term": {"entities": tag_one}},
                        {"term": {"entities": tag_two}}
                    ]
                }
            }
        }
    }

    return client.search(index=index,
                         doc_type=doc_type,
                         body=body,
                         size=size)['hits']['hits']

####################################################################################

def term_filter(term, from_offset=0, size=config.ELASTICSEARCH_RESULTS_SIZE, index=config.ELASTICSEARCH_INDEX, doc_type=config.ELASTICSEARCH_SENTENCE_TYPE):
    body = {
        "from": from_offset,
        "query": {
            "filtered": {
                "filter": {
                    "term": {"tokens": term}
                }
            }
        }
    }

    return client.search(index=index,
                         doc_type=doc_type,
                         body=body,
                         size=size)['hits']['hits']


def tagged_term_filter(term, tag, from_offset=0, size=config.ELASTICSEARCH_RESULTS_SIZE, index=config.ELASTICSEARCH_INDEX, doc_type=config.ELASTICSEARCH_SENTENCE_TYPE):
    body = {
        "from": from_offset,
        "query": {
            "filtered": {
                "filter": {
                    "term": {"tagged_tokens": "<%s>%s</%s>" % (tag,
                                                               term,
                                                               tag)}
                }
            }
        }
    }

    return client.search(index=index,
                         doc_type=doc_type,
                         body=body,
                         size=size)['hits']['hits']

####################################################################################

def get_page_by_id(page_id, index=config.ELASTICSEARCH_INDEX, doc_type=config.ELASTICSEARCH_PAGE_TYPE):
    return client.get(index=index,
                      id=page_id,
                      doc_type=doc_type)['_source']


def get_sentence_by_ids(page_id, sentence_index, index=config.ELASTICSEARCH_INDEX, doc_type=config.ELASTICSEARCH_SENTENCE_TYPE):
    return client.get(index=index,
                      id="%s_%s" % (page_id, sentence_index),
                      doc_type=doc_type)['_source']

def get_raw_sentence_by_ids(page_id, sentence_index, index=config.ELASTICSEARCH_INDEX, doc_type=config.ELASTICSEARCH_RAW_SENTENCE_TYPE):
    return client.get(index=index,
                      id="%s_%s" % (page_id, sentence_index),
                      doc_type=doc_type)['_source']
