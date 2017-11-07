from .seq import Seq
from .constants import ANY, ABSTRACT_GRAMMEMES


class PatternAbstract:
    max = None
    min = None

    def test(self, seq):
        return self.match(seq) != None


class PatternUnit(PatternAbstract):
    min = 1
    max = 1

    def __init__(self, grammeme):
        self.grammeme = grammeme

    def match(self, seq):
        if type(seq) == str: seq = Seq(seq)
        if len(seq) < self.min: return None
        found = seq[:1].constrain_find(self.grammeme)
        return (found, seq[1:]) if found else None


class PatternSeq(PatternAbstract):
    def __init__(self, *parts):
        self.parts = [(p if isinstance(p, PatternAbstract) else PatternUnit(p)) for p in parts]
        self.min = sum(p.min for p in self.parts)
        self.max = 0
        for p in self.parts:
            if p.max is None:
                self.max = None
                break
            self.max += p.max

    def match(self, seq):
        if type(seq) == str: seq = Seq(seq)
        if len(seq) < self.min: return None

        found = []
        for pattern in self.parts:
            if len(seq) < pattern.min: return None
            match = pattern.match(seq)
            if not match: return None
            more_found, seq = match
            found.append(more_found)

        return (sum(found) if found else Seq(), seq)


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

    def match(self, seq):
        if type(seq) == str: seq = Seq(seq)
        if len(seq) < self.min: return None
        for pattern in self.patterns:
            match = pattern.match(seq)
            if match:
                found, _ = match
                return (found, seq[len(found):])
        return None


class PatternAll(PatternAbstract):
    def __init__(self, *patterns):
        self.patterns = [(p if isinstance(p, PatternAbstract) else PatternUnit(p)) for p in patterns]
        self.min = max(v.min for v in self.patterns)
        self.max = 0
        for v in self.patterns:
            if v.max is None:
                self.max = None
                break
            self.max = max([self.max, v.max])

    def match(self, seq):
        if type(seq) == str: seq = Seq(seq)
        if len(seq) < self.min: return None
        found = seq
        for pattern in self.patterns:
            match = pattern.match(found)
            if not match: return None
            found, _ = match
        return (found, seq[len(found):])


class PatternRepeat(PatternAbstract):
    def __init__(self, pattern = ANY, min = 0, max = None):
        self.min_repeats = min
        self.max_repeats = max
        self.sub = pattern if isinstance(pattern, PatternAbstract) else PatternUnit(pattern)
        self.min = self.sub.min * self.min_repeats
        self.max = self.sub.max * self.max_repeats if self.sub.max and self.max_repeats else None

    def __getitem__(self, ix):
        return PatternRepeat(self.sub, ix.start or 0, ix.stop)

    def match(self, seq):
        if type(seq) == str: seq = Seq(seq)
        if len(seq) < self.min: return None
        max = self.max if self.max is not None else len(seq)

        found = []
        remains = seq
        while (len(remains)) > self.min and (not self.max_repeats or len(found) < self.max_repeats):
            match = self.sub.match(remains)
            if not match: break
            more_found, remains = match
            found.append(more_found)

        if len(found) < self.min_repeats: return None

        found = sum(found) or Seq()
        return (found, seq[len(found):])


class PatternSame(PatternAbstract):
    def __init__(self, grammemes, pattern):
        self.grammemes = [(ABSTRACT_GRAMMEMES[g] if g in ABSTRACT_GRAMMEMES else [g]) for g in grammemes]
        self.sub = pattern if isinstance(pattern, PatternAbstract) else PatternUnit(pattern)
        self.min = self.sub.min
        self.max = self.sub.max

    def match(self, seq):
        if type(seq) == str: seq = Seq(seq)
        if len(seq) < self.min: return None
        max = self.max if self.max is not None else len(seq)

        constrained = seq
        for alternatives in self.grammemes:
            candidate = Seq()
            for grm in alternatives:
                new_candidate = constrained.constrain_find(grm, max)
                if len(new_candidate) > len(candidate): candidate = new_candidate
            constrained = candidate

        match = self.sub.match(constrained)
        if match is None: return None
        found, _ = match
        return (found, seq[len(found):])