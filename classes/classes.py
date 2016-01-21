import math

from utils import rgx
from config import config


### CONTEXT #######################################################################

class Context:
    def __init__(self, tokens, weight):
        self.tokens = tokens
        self.weight = weight
        self.ctx = {}

        for token in self.tokens:
            if token in self.ctx:
                self.ctx[token] += 1
            else:
                self.ctx[token] = 1.0

        norm = math.sqrt(sum([pow(self.ctx[token], 2) for token in self.ctx]))

        for token in self.ctx:
            self.ctx[token] = weight * (self.ctx[token] / norm)


    def __getitem__(self, key):
        if key in self.ctx:
            return self.ctx[key]
        else:
            return 0.0


    def __add__(self, other):
        new_ctx = {}
        all_tokens = set(self.ctx.keys() + other.ctx.keys())
        
        for token in all_tokens:
            new_ctx[token] = self[token] + other[token]

        return AbstractContext(new_ctx)


    def __mul__(self, other):
        total = 0.0

        for token in self.ctx:
            total += self[token] * other[token]

        return total


    def __div__(self, factor):
        new_ctx = {}

        for token in self.ctx:
            new_ctx[token] = self[token] / factor

        return AbstractContext(new_ctx)


    def __eq__(self, other):
        return isinstance(other, Context) and self.tokens == other.tokens and self.weight == other.weight


    def __repr__(self):
        return "Context(tokens=%r, weight=%r)" % (self.tokens, self.weight)


class AbstractContext(Context):
    def __init__(self, ctx):
        self.ctx = ctx


    def __eq__(self, other):
        return isinstance(other, AbstractContext) and self.ctx == other.ctx


    def __repr__(self):
        return "AbstractContext(ctx=%r)" % self.ctx


### PATTERN #######################################################################

class Pattern:
    def __init__(self, left_ctx, tag_one, middle_ctx, tag_two, right_ctx):
        self.left_ctx = left_ctx
        self.tag_one = tag_one
        self.middle_ctx = middle_ctx
        self.tag_two = tag_two
        self.right_ctx = right_ctx


    def matching_tags(self, other):
        return self.tag_one == other.tag_one and self.tag_two == other.tag_two


    def match(self, other):
        if self.matching_tags(other):
            l = self.left_ctx * other.left_ctx
            m = self.middle_ctx * other.middle_ctx
            r = self.right_ctx * other.right_ctx
            return l + m + r
        else:
            return 0.0


    def __radd__(self, other): # to utilize sum()
        return self # assuming other is 0


    def __add__(self, other):
        if self.matching_tags(other):
            new_left_ctx = self.left_ctx + other.left_ctx
            new_middle_ctx = self.middle_ctx + other.middle_ctx
            new_right_ctx = self.right_ctx + other.right_ctx
            return Pattern(new_left_ctx,
                           self.tag_one,
                           new_middle_ctx,
                           self.tag_two,
                           new_right_ctx)
        else:
            # should never happen
            return self


    def __mul__(self, other):
        return self.match(other)


    def __div__(self, factor):
        new_left_ctx = self.left_ctx / factor
        new_middle_ctx = self.middle_ctx / factor
        new_right_ctx = self.right_ctx / factor
        return Pattern(new_left_ctx,
                       self.tag_one,
                       new_middle_ctx,
                       self.tag_two,
                       new_right_ctx)


    def __eq__(self, other):
        return isinstance(other, Pattern) and self.left_ctx == other.left_ctx and self.tag_one == other.tag_one and self.middle_ctx == other.middle_ctx and self.tag_two == other.tag_two and self.right_ctx == other.right_ctx


    def __repr__(self):
        return "Pattern(left_ctx=%r, tag_one=%r, middle_ctx=%r, tag_two=%r, right_ctx=%r)" % (self.left_ctx,
                                                                                              self.tag_one,
                                                                                              self.middle_ctx,
                                                                                              self.tag_two,
                                                                                              self.right_ctx)


class RawPattern(Pattern):
    def __init__(self, left_ctx, tag_one, middle_ctx, tag_two, right_ctx, page, index):
        Pattern.__init__(self, left_ctx, tag_one, middle_ctx, tag_two, right_ctx)
        self.page = page
        self.index = index


    def __eq__(self, other):
        return isinstance(other, RawPattern) and self.left_ctx == other.left_ctx and self.tag_one == other.tag_one and self.middle_ctx == other.middle_ctx and self.tag_two == other.tag_two and self.right_ctx == other.right_ctx and self.page == other.index and self.index == other.index


    def __repr__(self):
        return "RawPattern(left_ctx=%r, tag_one=%r, middle_ctx=%r, tag_two=%r, right_ctx=%r, page=%r, index=%r)" % (self.left_ctx,
                                                                                                                    self.tag_one,
                                                                                                                    self.middle_ctx,
                                                                                                                    self.tag_two,
                                                                                                                    self.right_ctx,
                                                                                                                    self.page,
                                                                                                                    self.index)


class SnowballPattern(Pattern):
    def __init__(self, support, pos, neg, update_factor=config.SNOWBALL_PATTERN_CONFIDENCE_UPDATE_FACTOR, old_conf=1.0):
        avg_pattern = sum(support) / len(support)

        Pattern.__init__(self,
                         avg_pattern.left_ctx,
                         avg_pattern.tag_one,
                         avg_pattern.middle_ctx,
                         avg_pattern.tag_two,
                         avg_pattern.right_ctx)
        
        self.support = support
        self.pos = pos
        self.neg = neg
        self.update_factor = update_factor
        self.old_conf = old_conf


    def confidence(self):
        return self.update_factor*self._confidence() + (1-self.update_factor)*self.old_conf

    def _confidence(self):
        return self.rlogf_confidence()
        

    def rlogf_confidence(self):
        return self.raw_confidence() * math.log(self.pos, 2)


    def raw_confidence(self):
        return float(self.pos) / (self.pos + self.neg)

    
    def update_confidence(self, tup, tuples):
        self.old_conf = self.confidence()

        for t in tuples:
            if tup.subj == t.subj:
                if tup.obj == t.obj:
                    self.pos += 1
                else:
                    self.neg += 1


    def __eq__(self, other):
        return isinstance(other, SnowballPattern) and self.left_ctx == other.left_ctx and self.tag_one == other.tag_one and self.middle_ctx == other.middle_ctx and self.tag_two == other.tag_two and self.right_ctx == other.right_ctx and self.support == other.support and self.pos == other.pos and self.neg == other.neg and self.update_factor == other.update_factor and self.old_conf == other.old_conf


    def __repr__(self):
        return "SnowballPattern(support=%r, pos=%r, neg=%r, update_factor=%r, old_conf=%r)" % (self.support,
                                                                                               self.pos,
                                                                                               self.neg,
                                                                                               self.update_factor,
                                                                                               self.old_conf)


### TUPLE #########################################################################

class Tuple:
    def __init__(self, rel, subj, obj, subj_tag, obj_tag):
        self.rel = rel
        self.subj = subj
        self.obj = obj
        self.subj_tag = subj_tag
        self.obj_tag = obj_tag


    def as_tuple(self):
        return (self.subj, self.obj)


    def subj_string(self):
        return u"<%s>%s</%s>" % (self.subj_tag,
                                 self.subj,
                                 self.subj_tag)


    def obj_string(self):
        return u"<%s>%s</%s>" % (self.obj_tag,
                                 self.obj,
                                 self.obj_tag)


    def __eq__(self, other):
        return isinstance(other, Tuple) and self.rel == other.rel and self.subj == other.subj and self.obj == other.obj and self.subj_tag == other.subj_tag and self.obj_tag == other.obj_tag


    def __hash__(self):
        return hash((self.rel,
                     self.subj,
                     self.obj,
                     self.subj_tag,
                     self.obj_tag))


    def __repr__(self):
        return "Tuple(rel=%r, subj=%r, obj=%r, subj_tag=%r, obj_tag=%r)" % (self.rel,
                                                                            self.subj,
                                                                            self.obj,
                                                                            self.subj_tag,
                                                                            self.obj_tag)


class CandidateTuple(Tuple):
    def __init__(self, rel, subj, obj, subj_tag, obj_tag, conf, update_factor=config.SNOWBALL_TUPLE_CONFIDENCE_UPDATE_FACTOR, patterns=None):
        Tuple.__init__(self, rel, subj, obj, subj_tag, obj_tag)
        self.conf = conf
        self.update_factor = update_factor
        self.patterns = patterns if patterns else []


    def add_pattern(self, pattern):
        self.patterns.append(pattern)


    def add_patterns(self, patterns):
        for p in patterns:
            self.add_pattern(p)


    def confidence(self):
        return self.conf

    
    def update_confidence(self, matches, snowball_patterns):
        vals = []
        max_conf = max([p.confidence() for p in snowball_patterns])
        
        for (similarity, pattern) in matches:
            vals.append(1 - similarity*(pattern.confidence() / max_conf))

        new_conf = 1 - reduce(lambda x, y: x*y, vals, 1.0)

        self.conf = self.update_factor*new_conf + (1-self.update_factor)*self.conf


    def __eq__(self, other):
        return isinstance(other, CandidateTuple) and self.rel == other.rel and self.subj == other.subj and self.obj == other.obj and self.subj_tag == other.subj_tag and self.obj_tag == other.obj_tag and self.conf == other.conf and self.update_factor == other.update_factor


    def __repr__(self):
        return "CandidateTuple(rel=%r, subj=%r, obj=%r, subj_tag=%r, obj_tag=%r, conf=%r, update_factor=%r, patterns=%r)" % (self.rel,
                                                                                                                             self.subj,
                                                                                                                             self.obj,
                                                                                                                             self.subj_tag,
                                                                                                                             self.obj_tag,
                                                                                                                             self.conf,
                                                                                                                             self.update_factor,
                                                                                                                             self.patterns)


### SENTENCE ######################################################################

class Sentence:
    def __init__(self, page, index, tokens, tagged_tokens):
        self.page = page
        self.index = index
        self.tokens = tokens
        self.tagged_tokens = tagged_tokens

    
    def index_combinations_by_tuple(self, tup):
        combos = []
        s1 = tup.subj_string()
        s2 = tup.obj_string()
        indices1 = [i for i in xrange(len(self.tagged_tokens)) if self.tagged_tokens[i] == s1]
        indices2 = [i for i in xrange(len(self.tagged_tokens)) if self.tagged_tokens[i] == s2]

        for i1 in indices1:
            for i2 in indices2:
                if i1 != i2:
                    combos.append((i1, i2))

        return combos

    
    def index_combinations_by_tags(self, subj_tag, obj_tag):
        combos = []
        r1 = rgx.create_template_rgx(subj_tag)
        r2 = rgx.create_template_rgx(obj_tag)
        indices1 = [i for i in xrange(len(self.tagged_tokens)) if r1.match(self.tagged_tokens[i])]
        indices2 = [i for i in xrange(len(self.tagged_tokens)) if r2.match(self.tagged_tokens[i])]

        for i1 in indices1:
            for i2 in indices2:
                if i1 != i2:
                    combos.append((i1, i2))

        return combos


    def preprocess_tokens(self, tokens):
        new_tokens = []

        for token in tokens:
            new_tokens.extend(token.split(u'_'))

        return new_tokens


    def extract_raw_patterns(self, tup):
        patterns = []
        combos = self.index_combinations_by_tuple(tup)

        for (i1, i2) in combos:
            i = i1 if i1 < i2 else i2
            j = i2 if i1 < i2 else i1
            tag_one = tup.subj_tag if i1 < i2 else tup.obj_tag
            tag_two = tup.obj_tag if i1 < i2 else tup.subj_tag

            left = self.tokens[:i]
            middle = self.tokens[i+1:j]
            right = self.tokens[j+1:]
            left_ctx = Context(self.preprocess_tokens(left)[-config.SNOWBALL_LR_MAX_WINDOW:],
                               config.SNOWBALL_LEFT_CTX_WEIGHT)
            middle_ctx = Context(self.preprocess_tokens(middle),
                                 config.SNOWBALL_MIDDLE_CTX_WEIGHT)
            right_ctx = Context(self.preprocess_tokens(right)[:config.SNOWBALL_LR_MAX_WINDOW],
                                config.SNOWBALL_RIGHT_CTX_WEIGHT)

            pattern = RawPattern(left_ctx, tag_one, middle_ctx, tag_two, right_ctx, self.page, self.index)

            patterns.append(pattern)

        return patterns


    def extract_candidate_tuples(self, rel, subj_tag, obj_tag):
        candidates = []
        combos = self.index_combinations_by_tags(subj_tag, obj_tag)

        for (i1, i2) in combos:
            i = i1 if i1 < i2 else i2
            j = i2 if i1 < i2 else i1
            tag_one = subj_tag if i1 < i2 else obj_tag
            tag_two = obj_tag if i1 < i2 else subj_tag

            left = self.tokens[:i]
            middle = self.tokens[i+1:j]
            right = self.tokens[j+1:]
            left_ctx = Context(self.preprocess_tokens(left)[-config.SNOWBALL_LR_MAX_WINDOW:],
                               config.SNOWBALL_LEFT_CTX_WEIGHT)
            middle_ctx = Context(self.preprocess_tokens(middle),
                                 config.SNOWBALL_MIDDLE_CTX_WEIGHT)
            right_ctx = Context(self.preprocess_tokens(right)[:config.SNOWBALL_LR_MAX_WINDOW],
                                config.SNOWBALL_RIGHT_CTX_WEIGHT)

            pattern = RawPattern(left_ctx, tag_one, middle_ctx, tag_two, right_ctx, self.page, self.index)

            subj = self.tokens[i1]
            obj = self.tokens[i2]
            tup = CandidateTuple(rel, subj, obj, subj_tag, obj_tag, 1.0, config.SNOWBALL_TUPLE_CONFIDENCE_UPDATE_FACTOR)

            candidates.append((tup, pattern))

        return candidates
            


    def __eq__(self, other):
        return isinstance(other, Sentence) and self.page == other.page and self.index == other.index and self.tokens == other.tokens and self.tagged_tokens == other.tagged_tokens


    def __repr__(self):
        return "Sentence(page=%r, index=%r, tokens=%r, tagged_tokens=%r)" % (self.page,
                                                                             self.index,
                                                                             self.tokens,
                                                                             self.tagged_tokens)


### CLUSTERING ####################################################################

class SinglePassClusteringAlgorithm:
    def __init__(self, patterns, threshold):
        self.patterns = patterns
        self.threshold = threshold
        self.clusters = []
        

    def calculate_rep(self, members):
        return sum(members) / len(members)


    def prepare(self):
        if len(self.patterns) != 0:
            first_cluster = {}
            first_cluster[u'members'] = [self.patterns[0]]
            first_cluster[u'rep'] = self.calculate_rep(first_cluster['members'])
            self.clusters.append(first_cluster)
            self.patterns = self.patterns[1:]


    def cluster(self):
        for pattern in self.patterns:
            cluster_matches = map(lambda c: (pattern.match(c['rep']), c),
                                  self.clusters)
            best_cluster_match = max(cluster_matches,
                                     key=lambda m: m[0])
            if best_cluster_match[0] >= self.threshold:
                best_cluster_match[1]['members'].append(pattern)
            else:
                new_cluster = {}
                new_cluster[u'members'] = [pattern]
                new_cluster[u'rep'] = self.calculate_rep(new_cluster[u'members'])
                self.clusters.append(new_cluster)


    def get_snowball_patterns(self):
        snowball_patterns = []
        
        for cluster in self.clusters:            
            if len(cluster['members']) >= config.SNOWBALL_MIN_PATTERN_SUPPORT:
                pattern = SnowballPattern(cluster['members'],
                                          len(cluster['members']),
                                          0,
                                          config.SNOWBALL_PATTERN_CONFIDENCE_UPDATE_FACTOR)
                
                snowball_patterns.append(pattern)

        return snowball_patterns


### MAIN ##########################################################################

def main():
    pass


if __name__ == "__main__":
    main()
