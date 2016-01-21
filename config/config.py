import os
import logging

# Home
HOME_DIR = os.getenv("HOME")

# Directory for non-code resource files
RESOURCES_DIR = "%s/resources" % HOME_DIR

# Stanford CoreNLP settings
STANFORD_CORENLP_DIR = "%s/stanford-corenlp-full-2015-04-20/*" % RESOURCES_DIR

# Stanford parser settings
STANFORD_PARSER_DIR = "%s/stanford-parser-full-2015-04-20" % RESOURCES_DIR
STARFORD_PARSER_JAR_FILE = "%s/stanford-parser.jar" % STANFORD_PARSER_DIR
STARFORD_PARSER_MODELS_JAR_FILE = "%s/stanford-parser-3.5.2-models.jar" % STANFORD_PARSER_DIR

# Elasticsearch settings
ELASTICSEARCH_HOST = 'localhost'
ELASTICSEARCH_PORT = 9200
ELASTICSEARCH_RESULTS_SIZE = 100
ELASTICSEARCH_INDEX = 'wikipedia_test'
ELASTICSEARCH_PAGE_TYPE = 'page'
ELASTICSEARCH_SENTENCE_TYPE = 'sentence'
ELASTICSEARCH_RAW_SENTENCE_TYPE = 'raw_sentence'
ELASTICSEARCH_PAGE_MAPPING_FILE = "%s/mappings/page.json" % RESOURCES_DIR
ELASTICSEARCH_SENTENCE_MAPPING_FILE = "%s/mappings/sentence.json" % RESOURCES_DIR
ELASTICSEARCH_RAW_SENTENCE_MAPPING_FILE = "%s/mappings/raw_sentence.json" % RESOURCES_DIR

# Wikipedia related variables
WIKIPEDIA_DIR = "%s/wikipedia" % RESOURCES_DIR
WIKIPEDIA_DUMP_DIR = "%s/dumps" % WIKIPEDIA_DIR
WIKIPEDIA_DUMP = "%s/enwiki-20150602-pages-articles.xml.bz2" % WIKIPEDIA_DUMP_DIR
WIKIPEDIA_EXTRACTED_DIR = "%s/extracted2" % WIKIPEDIA_DIR
WIKIPEDIA_SUB_DIR_PREFIXES = []
WIKIPEDIA_START_TAG_RGX = "^<doc id=\".*\" url=\".*\" title=\".*\">\n$"
WIKIPEDIA_END_TAG_RGX = "^</doc>\n?$"

# Logging settings
LOGS_DIR = "%s/logs" % RESOURCES_DIR
LOGGER_FORMAT = "%(levelname)s (%(name)s): %(message)s"
LOGGER_DEFAULT_LVL = logging.INFO

# Snowball settings
SNOWBALL_RESOURCE_DIR = "%s/snowball" % RESOURCES_DIR
SNOWBALL_CURRENT_RUN_DIR = "%s/<some_name>" % SNOWBALL_RESOURCE_DIR
SNOWBALL_SEEDS_FILE = "%s/seeds" % SNOWBALL_CURRENT_RUN_DIR
SNOWBALL_TUPLES_FILE = "%s/tuples" % SNOWBALL_CURRENT_RUN_DIR
SNOWBALL_PATTERNS_FILE = "%s/patterns" % SNOWBALL_CURRENT_RUN_DIR
SNOWBALL_SENTENCE_CAP = 10000 # how many text segments to consider
SNOWBALL_LR_MAX_WINDOW = 2 # maximum number of tokens in left/right contexts
SNOWBALL_LEFT_CTX_WEIGHT = 0.1#0.2 # weight for left context
SNOWBALL_MIDDLE_CTX_WEIGHT = 0.8#0.6 # weight for middle context
SNOWBALL_RIGHT_CTX_WEIGHT = 0.1#0.2 # weight for right context
SNOWBALL_NUM_ITERATIONS = 10 # number of iterations to perform
SNOWBALL_MIN_PATTERN_SUPPORT = 2 # minimum number of patterns per cluster
SNOWBALL_MIN_TUPLE_CONFIDENCE = 0.8#0.8 # minimum acceptable tuple confidence
SNOWBALL_MIN_PATTERN_SIMILARITY = 0.6#0.6 # minimum degree of match for patterns
SNOWBALL_PATTERN_CONFIDENCE_UPDATE_FACTOR = 0.5 # factor to use in EWMA
SNOWBALL_TUPLE_CONFIDENCE_UPDATE_FACTOR = 0.5 # factor to use in EWMA
