from .seq import Seq
from .constants import ANY, ABSTRACT_GRAMMEMES


class Match(object):
    __slots__ = ('seq', 'groups')

    def __init__(self, seq, groups = {}):
        self.seq    = seq
        self.groups = groups

    def __add__(self, other):
        return Match(self.seq + other.seq, Match.merge_groups(self.groups, other.groups))

    def __repr__(self):
        seq_repr = ' '.join(w.__repr__() for w in self.seq.words)

        count    = 0
        for n, g in self.groups.items(): count += len(g)
        grp_repr = (' / ' + str(count) + 'g') if len(self.groups) else ''

        return 'Match(' + seq_repr + grp_repr + ')'

    @staticmethod
    def merge_groups(gs1, gs2):
        if len(gs1) and len(gs2):
            gs3 = {}
            for name, group in gs1.items():
                if name in gs2 and len(gs2[name]):
                    gs3[name] = list(group) # will be extended, should copy
                else:
                    gs3[name] = group
            for name, group in gs2.items():
                if name not in gs3: gs3[name] = gs2[name]
                else: gs3[name] = gs1[name] + gs2[name]
        else:
            gs3 = gs1 or gs2

        return gs3


class PatternAbstract(object):
    __slots__ = tuple()

    def match(self, seq):
        if type(seq) == str: seq = Seq(seq)
        for match in self.match_gen(seq): return match

    def test(self, seq):
        for match in self.match_gen(seq): return match != None


class PatternUnit(PatternAbstract):
    __slots__ = ('min', 'max', 'grammeme')

    def __init__(self, grammeme):
        self.min = 1
        self.max = 1
        self.grammeme = grammeme

    def match_gen(self, seq, lvl = 0):
        if len(seq) < self.min: return
        found = seq[:1].constrain_find(self.grammeme)
        if found: yield Match(found)


class PatternWord(PatternAbstract):
    __slots__ = ('min', 'max', 'word')

    def __init__(self, word):
        self.min = 1
        self.max = 1
        self.word = word

    def match_gen(self, seq, lvl = 0):
        if not len(seq): return
        if seq[0].text == self.word: yield Match(seq[:1])


class PatternLexeme(PatternAbstract):
    __slots__ = ('min', 'max', 'normal_form')

    def __init__(self, normal_form):
        self.min = 1
        self.max = 1
        self.normal_form = normal_form

    def match_gen(self, seq, lvl = 0):
        if not len(seq): return
        word = seq.words[0].constrain_normal_form(self.normal_form)
        if word: yield Match(Seq.from_words([word]))


class PatternAny(PatternAbstract):
    __slots__ = ('min', 'max', 'patterns')

    def __init__(self, *patterns):
        self.patterns = [(p if isinstance(p, PatternAbstract) else PatternUnit(p)) for p in patterns]
        self.min = min(v.min for v in self.patterns)
        self.max = 0
        for v in self.patterns:
            if v.max is None:
                self.max = None
                break
            self.max = max([self.max, v.max])

    def match_gen(self, seq, lvl = 0):
        if len(seq) < self.min: return
        for pattern in self.patterns:
            for match in pattern.match_gen(seq, lvl + 1):
                yield match


class PatternAll(PatternAbstract):
    __slots__ = ('min', 'max', 'first', 'rest', 'patterns')

    def __init__(self, *patterns):
        self.patterns = [(p if isinstance(p, PatternAbstract) else PatternUnit(p)) for p in patterns]
        self.first    = self.patterns[0]
        self.rest     = PatternAll(*self.patterns[1:]) if len(self.patterns) > 1 else None
        self.min      = max(v.min for v in self.patterns)
        self.max      = 0
        for v in self.patterns:
            if v.max is None:
                self.max = None
                break
            self.max = max([self.max, v.max])

    def match_gen(self, seq, lvl = 0):
        if len(seq) < self.min: return
        for match_first in self.first.match_gen(seq, lvl + 1):
            if not self.rest:
                yield match_first
            else:
                for match_rest in self.rest.match_gen(match_first.seq, lvl + 1):
                    groups = Match.merge_groups(match_first.groups, match_rest.groups)
                    yield Match(match_rest.seq, groups)


class PatternSeq(PatternAbstract):
    __slots__ = ('min', 'max', 'first', 'rest', 'parts')

    def __init__(self, *parts):
        self.parts = [(p if isinstance(p, PatternAbstract) else PatternUnit(p)) for p in parts]
        self.first = self.parts[0]
        self.rest  = PatternSeq(*self.parts[1:]) if len(self.parts) > 1 else None
        self.min = sum(p.min for p in self.parts)
        self.max = 0
        for p in self.parts:
            if p.max is None:
                self.max = None
                break
            self.max += p.max

    def match_gen(self, seq, lvl = 0):
        if len(seq) < self.min: return

        for match_head in self.first.match_gen(seq, lvl + 1):
            if not self.rest:
                yield match_head
            else:
                for match_tail in self.rest.match_gen(seq[len(match_head.seq):], lvl + 1):
                    yield match_head + match_tail


class PatternRepeat(PatternAbstract):
    __slots__ = ('min', 'max', 'min_repeats', 'max_repeats', 'sub', '__rest')

    def __init__(self, pattern = ANY, min = 0, max = None):
        self.__rest      = None
        self.min_repeats = min
        self.max_repeats = max
        self.sub = pattern if isinstance(pattern, PatternAbstract) else PatternUnit(pattern)
        self.min = self.sub.min * self.min_repeats
        self.max = self.sub.max * self.max_repeats if self.sub.max != None and self.max_repeats != None else None

    def __getitem__(self, ix):
        return PatternRepeat(self.sub, ix.start or 0, ix.stop)

    def match_gen(self, seq, lvl = 0):
        if len(seq) < self.min: return
        if self.max_repeats == 0: return

        for match_head in self.sub.match_gen(seq, lvl + 1):
            should_try_more  = \
                len(seq) > len(match_head.seq) \
                and (len(seq) - len(match_head.seq) >= self.min - self.sub.min) \
                and (self.max_repeats is None or self.max_repeats > 1)
            must_try_more = self.min_repeats > 1

            if should_try_more:
                for match_tail in self.rest.match_gen(seq[len(match_head.seq):], lvl + 1):
                    yield match_head + match_tail
            elif not must_try_more:
                yield match_head

        if self.min_repeats == 0:
            yield Match(Seq())

    @property
    def rest(self):
        if self.__rest is None:
            if self.min_repeats == 0 and self.max_repeats is None:
                self.__rest = self
            else:
                self.__rest = PatternRepeat(
                    self.sub,
                    max(self.min_repeats - 1, 0),
                    max(self.max_repeats - 1, 0) if self.max_repeats != None else None
                )
        return self.__rest


class PatternMaybe(PatternRepeat):
    __slots__ = ('min', 'max', 'min_repeats', 'max_repeats', 'sub', '__rest')

    def __init__(self, pattern):
        super().__init__(pattern, min = 0, max = 1)


class PatternSame(PatternAbstract):
    __slots__ = ('min', 'max', 'sub', 'grms', 'rest')

    def __init__(self, grms, pattern):
        self.grms   = [(ABSTRACT_GRAMMEMES[g] if g in ABSTRACT_GRAMMEMES else [g]) for g in grms]
        self.rest   = PatternSame(grms[1:], pattern) if len(grms) > 1 else None
        self.sub    = pattern if isinstance(pattern, PatternAbstract) else PatternUnit(pattern)
        self.min    = self.sub.min
        self.max    = self.sub.max

    def match_gen(self, seq, lvl = 0):
        if len(seq) < self.min: return
        constrained = self.constrain_same(seq)
        for constrained in self.constrain_same(seq, lvl):
            for match in self.sub.match_gen(constrained, lvl + 1):
                yield match

    def constrain_same(self, seq, lvl = 0):
        max = self.max if self.max is not None else len(seq)

        alternatives = []
        for grm in self.grms[0]:
            alternative = seq.constrain_find(grm, max)
            if len(alternative) and len(alternative) >= self.min:
                alternatives.append(alternative)
        alternatives.sort(key = len, reverse = True)

        for alternative in alternatives:
            if self.rest:
                for alternative in self.rest.constrain_same(alternative, lvl + 1):
                    if len(alternative): yield alternative
            else:
                yield alternative

        yield Seq()

class PatternNamed(PatternAbstract):
    __slots__ = ('min', 'max', 'sub', 'name')

    def __init__(self, name, pattern):
        self.sub  = pattern if isinstance(pattern, PatternAbstract) else PatternUnit(pattern)
        self.name = name
        self.min  = self.sub.min
        self.max  = self.sub.max

    def match_gen(self, seq, lvl = 0):
        name = self.name
        for match in self.sub.match_gen(seq):
            groups = {self.name: [match.seq]}
            yield Match(match.seq, groups)
