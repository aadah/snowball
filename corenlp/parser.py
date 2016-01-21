import xmltodict
import collections
import nltk
import nltk.data
from nltk.parse.stanford import StanfordParser
from pprint import pprint

from stanford_corenlp_pywrapper import CoreNLP
from config import config
from utils import io, rgx


def get_tree_parser():
    tree_parser = StanfordParser(path_to_jar=config.STARFORD_PARSER_JAR_FILE,
                            path_to_models_jar=config.STARFORD_PARSER_MODELS_JAR_FILE)

    return tree_parser


def parse_sent(sent, tree_parser):
    tokens = nltk.word_tokenize(sent)

    return tree_parser.parse_one(tokens)


def has_is_a_relation(tree):
    verb_tags = ['VB', 'VBZ', 'VBP', 'VBD', 'VBN', 'VBG']
    verbs = ['be', 'is', 'was', 'are', 'were', 'been']

    if tree.label() == 'ROOT': tree = tree[0]

    vps = collections.deque()

    # dfs search
    push = vps.appendleft
    epush = vps.extendleft
    pop = vps.pop

    for subtree in tree:
        if subtree.label() == 'VP':
            push(subtree)
        elif subtree.label() == 'S':
            # edge cases from incorrectly spaced sentences
            if has_is_a_relation(subtree):
                return True

    while len(vps) != 0:
        vp = pop()
        new_vps = []

        for subtree in vp:
            if subtree.label() in verb_tags:
                labels = set([st.label() for st in vp])
                if subtree[0] in verbs and 'NP' in labels and 'VP' not in labels:
                    return True
            elif subtree.label() == 'VP':
                new_vps.append(subtree)

        epush(new_vps)

    return False


def get_sentence_tokenizer():
    sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    return sent_tokenizer


def text_to_sentences(text, sent_tokenizer):
    return sent_tokenizer.tokenize(text)


def get_parser():
    corenlp = CoreNLP(
        configdict={
            'annotators': 'tokenize,ssplit,pos,lemma,ner'
        },
        output_types=['ssplit','ner'],
        corenlp_jars=[config.STANFORD_CORENLP_DIR])

    return corenlp


def parse(text, corenlp):
    """Main function for CoreNLP parser."""

    return corenlp.parse_doc(text)


def scan_next(f):
    """Given the handler of the
    plain text wikipedia file,
    returns the xml parse of the
    next page to be read, or None
    if the end has been reached."""
    
    head = ''
    tail = ''
    lines = []
    started = False

    while True:
        line = f.readline()
        if line == '': return (None, None)
        if rgx.page_start(line):
            head = line
            started = True
        elif rgx.page_end(line):
            tail = line
            break
        elif started:
            lines.append(line)

    return (xmltodict.parse(head+tail),
            io.to_unicode(''.join(lines)))


def get_page(xml):
    """Given an XML parse xml, returns
    a dictionary of containing
    the page id, url, and title,
    as well as the raw title from
    the url."""

    page = {}

    page[u'id'] = int(xml['doc']['@id'])
    page[u'url'] = xml['doc']['@url']
    page[u'title'] = xml['doc']['@title']
    page[u'title_not_analyzed'] = page['title']
    
    return page


def collapse(sent):
    """Given a sentence dictionary,
    returns a list of tokens grouped
    by their named entity tagging."""

    new_tokens = []
    tagged_tokens = []
    cur_token = None
    cur_entity = u'O'
    tagging_pattern = "<%s>%s</%s>"
    tokens = sent['tokens']
    entities = sent['ner']
    pairs = zip(tokens, entities)

    for (t, e) in pairs:
        if cur_entity == u'O':
            if e == u'O':
                new_tokens.append(t)
                tagged_tokens.append(t)
            else:
                cur_token = t
                cur_entity = e
        else:
            if e == u'O':
                new_tokens.append(cur_token)
                new_tokens.append(t)
                tagged_tokens.append(tagging_pattern % (cur_entity,
                                                        cur_token,
                                                        cur_entity))
                tagged_tokens.append(t)
                cur_token = None
                cur_entity = u'O'
            elif e == cur_entity:
                cur_token += '_%s' % t
            else:
                new_tokens.append(cur_token)
                tagged_tokens.append(tagging_pattern % (cur_entity,
                                                        cur_token,
                                                        cur_entity))
                cur_token = t
                cur_entity = e
                
    return (new_tokens, tagged_tokens)


def simplify_sentence(sent):
    """Given a sentence from the
    CoreNLP parse, returns a more
    concise version."""

    new_sent = {}
    (tokens, tagged_tokens) = collapse(sent)

    new_sent[u'tokens'] = tokens
    new_sent[u'tagged_tokens'] = tagged_tokens
    new_sent[u'entities'] = list(set(sent['ner']))
    
    return new_sent


def get_sentences(text, corenlp):
    """Given an XML parse xml,
    returns a list a dictionaries
    each of which are represententions
    of the sentences from the xml text."""

    new_sents = []
    sents = parse(text, corenlp)['sentences']
    
    for i in xrange(len(sents)):
        new_sent = simplify_sentence(sents[i])
        new_sent[u'index'] = i
        new_sents.append(new_sent)

    return new_sents


def combined_parse(xml, text, corenlp):
    """Returns a dictionary where
    'page' maps to the page dictionary
    and 'sentences' maps to a list of
    simplified sentences."""

    combined_parse = {}
    page = get_page(xml)
    sentences = get_sentences(text, corenlp)

    for sent in sentences:
        sent[u'id'] = page['id']

    combined_parse[u'page'] = page
    combined_parse[u'sentences'] = sentences

    return combined_parse
