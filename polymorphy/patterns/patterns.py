from ..seq import Seq
from ..constants import ANY, ABSTRACT_GRAMMEMES


class PatternAbstract:
    max = None
    min = None

    def match(self, seq):
        if type(seq) == str: seq = Seq(seq)
        for match in self.match_gen(seq): return match

    def test(self, seq):
        for match in self.match_gen(seq): return match != None


class PatternUnit(PatternAbstract):
    min = 1
    max = 1

    def __init__(self, grammeme):
        self.grammeme = grammeme

    def match_gen(self, seq, lvl = 0):
        if len(seq) < self.min: return
        found = seq[:1].constrain_find(self.grammeme)
        if found: yield found


class PatternWord(PatternAbstract):
    min = 1
    max = 1
    def __init__(self, word):
        self.word = word

    def match_gen(self, seq, lvl = 0):
        if not len(seq): return
        if seq[0].text == self.word: yield seq[:1]


class PatternLexem(PatternAbstract):
    min = 1
    max = 1
    def __init__(self, normal_form):
        self.normal_form = normal_form

    def match_gen(self, seq, lvl = 0):
        if not len(seq): return
        word = seq.words[0].constrain_normal_form(self.normal_form)
        if word: yield Seq.from_words([word])


class PatternSeq(PatternAbstract):
    __rest = None

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
                for match_tail in self.rest.match_gen(seq[len(match_head):], lvl + 1):
                    yield match_head + match_tail


class PatternAny(PatternAbstract):
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
    def __init__(self, *patterns):
        patterns   = [(p if isinstance(p, PatternAbstract) else PatternUnit(p)) for p in patterns]
        self.first = patterns[0]
        self.rest  = PatternAll(*patterns[1:]) if len(patterns) > 1 else None
        self.min   = max(v.min for v in patterns)
        self.max   = 0
        for v in patterns:
            if v.max is None:
                self.max = None
                break
            self.max = max([self.max, v.max])

    def match_gen(self, seq, lvl = 0):
        if len(seq) < self.min: return
        for match in self.first.match_gen(seq, lvl + 1):
            if not self.rest:
                yield match
            else:
                for match in self.rest.match_gen(match, lvl + 1):
                    yield match


class PatternRepeat(PatternAbstract):
    __rest = None

    def __init__(self, pattern = ANY, min = 0, max = None):
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
                len(seq) > len(match_head) \
                and (len(seq) - len(match_head) >= self.min - self.sub.min) \
                and (self.max_repeats is None or self.max_repeats > 1)
            must_try_more = self.min_repeats > 1

            if should_try_more:
                for match_tail in self.rest.match_gen(seq[len(match_head):], lvl + 1):
                    yield match_head + match_tail
            elif not must_try_more:
                yield match_head

        if self.min_repeats == 0:
            yield Seq()

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


class PatternSame(PatternAbstract):
    __rest = None

    def __init__(self, grms, pattern):
        self.grms = [(ABSTRACT_GRAMMEMES[g] if g in ABSTRACT_GRAMMEMES else [g]) for g in grms]
        self.rest = PatternSame(grms[1:], pattern) if len(grms) > 1 else None
        self.sub  = pattern if isinstance(pattern, PatternAbstract) else PatternUnit(pattern)
        self.min  = self.sub.min
        self.max  = self.sub.max

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
