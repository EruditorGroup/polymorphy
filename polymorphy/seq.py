import re
from .constants import ANY
from .word import Word


# Предложение - последовательность слов.
class Seq:
    __spaces_pattern = re.compile(r'[\s]+')
    __text = None

    def __init__(self, text = ''):
        self.words = [Word(w) for w in Seq.__spaces_pattern.split(text) if len(w)]

    def __eq__(self, other):
        if not isinstance(other, Seq): return False
        return self.words == other.words

    def __bool__(self):
        return len(self.words) > 0

    def __iter__(self):
        return (w for w in self.words)

    def __len__(self):
        return len(self.words)

    def __contains__(self, item):
        return any(w.text == item for w in self.words)

    def __getitem__(self, ix):
        if type(ix) == int: return self.words[ix]
        seq = Seq.__new__(Seq)
        seq.words = self.words[ix]
        return seq

    def __add__(self, other):
        if not other: return self
        if type(other) == str: other = Seq(other)
        words = []
        for word in self.words:  words.append(word)
        for word in other.words: words.append(word)
        return Seq.from_words(words)

    def __radd__(self, other):
        if not other: return self
        if type(other) == str: other = Seq(other)
        return other + self

    def __repr__(self):
        return 'Seq(' + ' '.join(w.__repr__() for w in self.words) + ')'

    @property
    def text(self):
        if self.__text is None: self.__text = ' '.join(w.text for w in self.words)
        return self.__text

    @staticmethod
    def from_words(words):
        seq = Seq.__new__(Seq)
        seq.words = words
        return seq

    # Возвращает копию предложения, в которой все варианты слов содержат указанную граммему.
    # Возвращает None, если хотя бы одно слово не содержит граммему.
    def constrain(self, grammeme):
        if grammeme == ANY: return self
        words = []
        for word in self.words:
            word = word.constrain(grammeme)
            if word is None: return None
            words.append(word)
        return Seq.from_words(words)

    # Возвращает часть последовательности, ограниченную по граммеме
    def constrain_find(self, grammeme, max = None):
        if max is None: max = len(self.words)
        words = []
        for word in self.words:
            if len(words) > max: break
            word = word.constrain(grammeme)
            if word is None: break
            words.append(word)
        return Seq.from_words(words)
