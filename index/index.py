import argparse
import logging

from utils import io, log, parallel
from corenlp import parser
from elastic import es
from config import config


class IndexWorker(parallel.Worker):
    def __init__(self, queue, corenlp, logger):
        parallel.Worker.__init__(self)
        self.queue = queue
        self.corenlp = corenlp
        self.logger = logger


    def work(self):
        self.logger.debug("Process %d has begun.", self.process.pid)

        while True:

            # path of next extracted file
            path = self.queue.get()
            self.logger.info('Now processing file: %s', path)
            
            # acquire file handler
            with open(path, 'r') as f:

                # loop while a doc is available
                (xml, text) = parser.scan_next(f)
                while xml:

                    # parse
                    parse = parser.combined_parse(xml, text, self.corenlp)
                    page = parse['page']
                    sentences = parse['sentences']

                    # index
                    es.index_page(page)
                    for sentence in sentences:
                        es.index_sentence(sentence)

                    self.logger.debug("Indexed article %d: \"%s\"",
                                      page['id'],
                                      page['title'])

                    # continue
                    (xml, text) = parser.scan_next(f)
            
            # notify queue
            self.queue.task_done()
            self.logger.info('Done processing file: %s', path)


def main(args):
    print "Running..."

    # get extracted wikipedia file pathnames
    subdirs = io.list_directories(config.WIKIPEDIA_EXTRACTED_DIR)
    if args.letters:
        subdirs = [p for p in subdirs if p[-2] in config.WIKIPEDIA_SUB_DIR_PREFIXES]
    pathnames = []
    for sb in subdirs:
        pathnames.extend(io.list_files(sb))
    pathnames.sort()
    
    # create thread-safe queue
    queue = parallel.create_queue(pathnames)

    # create corenlp process
    corenlp = parser.get_parser()

    # create workers
    workers = []
    for i in xrange(args.threads):
        logger = log.create_logger('LOGGER %d' % i, 'log_%d.log' % i)
        if args.verbose:
            logger.setLevel(logging.DEBUG)
        worker = IndexWorker(queue, corenlp, logger)
        workers.append(worker)

    # begin
    for worker in workers:
        worker.start()

    # block until all files have been processed
    queue.join()

    print "Done!"


def main2(args):
    print "Running..."

    # get extracted wikipedia file pathnames
    subdirs = io.list_directories(config.WIKIPEDIA_EXTRACTED_DIR)
    if args.letters:
        subdirs = [p for p in subdirs if p[-2] in config.WIKIPEDIA_SUB_DIR_PREFIXES]
    pathnames = []
    for sb in subdirs:
        pathnames.extend(io.list_files(sb))
    pathnames.sort()
    
    # create thread-safe queue
    queue = parallel.create_queue(pathnames)

    # create workers
    workers = []
    for i in xrange(args.threads):
        logger = log.create_logger('LOGGER %d' % i, 'log_%d.log' % i)
        sent_tokenizer = parser.get_sentence_tokenizer()
        if args.verbose:
            logger.setLevel(logging.DEBUG)
        worker = SentenceIndexWorker(queue, sent_tokenizer, logger)
        workers.append(worker)

    # begin
    for worker in workers:
        worker.start()

    # block until all files have been processed
    queue.join()

    print "Done!"


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()

    argparser.add_argument('-l', '--letters',
                           action='store_true',
                           help='Only subdirectories beginning with one of the letters in config')

    argparser.add_argument('-t', '--threads',
                           default=2,
                           type=int,
                           help='Number of threads used to index')

    argparser.add_argument('-v', '--verbose',
                           action='store_true',
                           help='Whether to used verbose logging')

    args = argparser.parse_args()

    main(args)
