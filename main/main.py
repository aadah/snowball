from utils import io, log
from classes import classes
from elastic import es
from config import config

from pprint import pprint


def main():
    print "Running . . ."

    # initialize seeds/patterns list
    seeds = []
    snowball_patterns = []
    seed_dict = io.parse_seed_file(config.SNOWBALL_SEEDS_FILE)
    tuples = []

    # output tuples/patterns files + main logger
    tuples_f = open(config.SNOWBALL_TUPLES_FILE, 'a')
    patterns_f = open(config.SNOWBALL_PATTERNS_FILE, 'a')
    logger = log.create_logger("snowball", "snowball.log")

    # partition sentence search space by iteration
    sentence_count = config.SNOWBALL_SENTENCE_CAP
    sentences_per_iter = sentence_count / config.SNOWBALL_NUM_ITERATIONS
    remainder = sentence_count % config.SNOWBALL_NUM_ITERATIONS
    counts = [sentences_per_iter] * config.SNOWBALL_NUM_ITERATIONS
    counts[-1] += remainder # tack on remainder

    # create initial seed and tuple sets
    for (subj, obj) in seed_dict['pairs']:
        tup = classes.CandidateTuple(seed_dict['rel'],
                                     subj,
                                     obj,
                                     seed_dict['subj_tag'],
                                     seed_dict['obj_tag'],
                                     1.0)
        seeds.append(tup)
        tuples.append(tup)
        
    # some info on seeds and relation settings
    logger.info("Relation: %r, Subject tag: %r, Object Tag: %r",
                seed_dict['rel'],
                seed_dict['subj_tag'],
                seed_dict['obj_tag'])
    logger.info("Seeds: %r", seed_dict['pairs'])

    # begin
    for i in xrange(config.SNOWBALL_NUM_ITERATIONS):
        logger.info("Beginning iteration %r", i+1)

        raw_patterns = []
        candidate_tuples = {tup: {'matches': [],
                                  'raw_patterns': []} for tup in seeds}

        logger.info("PATTERN EXTRACTION PHASE")

        # retrieve sentences / extract raw patterns
        logger.info("Retrieving sentences and extracting raw patterns . . .")
        for tup in seeds:
            count = es.count_sentences_containing(tup)
            hits = es.get_sentences_containing(tup, 0, count)
            
            for hit in hits:
                source = hit['_source']
                sent = classes.Sentence(source['id'],
                                        source['index'],
                                        source['tokens'],
                                        source['tagged_tokens'])
                raw_patterns.extend(sent.extract_raw_patterns(tup))

        logger.info("Number of raw patterns: %d", len(raw_patterns))
        
        # cluster raw patterns
        logger.info("Clustering raw patterns . . .")
        clusterer = classes.SinglePassClusteringAlgorithm(raw_patterns,
                                                          config.SNOWBALL_MIN_PATTERN_SIMILARITY)
        clusterer.prepare()
        clusterer.cluster()

        new_snowball_patterns = clusterer.get_snowball_patterns()

        if len(new_snowball_patterns) == 0:
            logger.info("No new patterns. Prematurely exiting on iteration %d", i+1)
            break

        snowball_patterns.extend(new_snowball_patterns)        
        
        logger.info("Total number of patterns: %d", len(snowball_patterns))

        logger.info("Writing new patterns to: %r", config.SNOWBALL_TUPLES_FILE)
        for pat in new_snowball_patterns:
            io.write_line(patterns_f, pat)

        logger.info("TUPLE EXTRACTION PHASE")

        logger.info("Searching through sentences . . .")

        # retrieve sentences one at a time to avoid blowing up memory
        for j in xrange(counts[i]):
            from_offset = j + i*sentences_per_iter
            source = es.get_sentences_with_tags(seed_dict['subj_tag'],
                                                seed_dict['obj_tag'],
                                                from_offset,
                                                1)[0]['_source']
            sent = classes.Sentence(source['id'],
                                    source['index'],
                                    source['tokens'],
                                    source['tagged_tokens'])
            candidates = sent.extract_candidate_tuples(seed_dict['rel'],
                                                       seed_dict['subj_tag'],
                                                       seed_dict['obj_tag'])

            for (candidate, raw_pattern) in candidates:
                best_similarity = 0.0
                best_pattern = None

                for sb_pattern in snowball_patterns:
                    similarity = sb_pattern.match(raw_pattern)

                    if similarity >= config.SNOWBALL_MIN_PATTERN_SIMILARITY:
                        sb_pattern.update_confidence(candidate, seeds)

                        if similarity >= best_similarity:
                            best_similarity = similarity
                            best_pattern = sb_pattern

                if best_similarity >= config.SNOWBALL_MIN_PATTERN_SIMILARITY:
                    if candidate not in candidate_tuples:
                        candidate_tuples[candidate] = {'matches': [],
                                                       'raw_patterns': []}
                    candidate_tuples[candidate]['matches'].append((best_similarity,
                                                                       best_pattern))
                    candidate_tuples[candidate]['raw_patterns'].append(raw_pattern)

        new_tuples = candidate_tuples.keys()

        logger.info("Number of candidate tuples: %d", len(new_tuples))

        for new_tuple in new_tuples:
            new_tuple.update_confidence(candidate_tuples[new_tuple]['matches'], snowball_patterns)
            new_tuple.add_patterns(candidate_tuples[new_tuple]['raw_patterns'])

        seeds = [tup for tup in new_tuples if tup.confidence() >= config.SNOWBALL_MIN_TUPLE_CONFIDENCE]

        if len(seeds) == 0:
            logger.info("No new seeds. Prematurely exiting on iteration %d", i+1)
            break

        tuples.extend(seeds) # store everything

        logger.info("Number of seed tuples: %d", len(seeds))

        logger.info("Total tuples so far (roughly): %d", len(tuples))

        logger.info("Ending iteration %d", i+1)

    logger.info("Writing tuples to: %r", config.SNOWBALL_TUPLES_FILE)
    for tup in tuples:
        io.write_line(tuples_f, tup)

    # close files
    tuples_f.close()
    patterns_f.close()

    print "Done!"


if __name__ == '__main__':
    main()
