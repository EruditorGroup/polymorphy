import pymorphy2
from .constants import ANY, ABSTRACT_GRAMMEMES, POS


# Слово представляет строку + набор вариантов его интерпретации с помощью pymorphy2.MorphAnalyzer.
class Word:
    __morph = pymorphy2.MorphAnalyzer()
    __variants = None

    def __init__(self, text, threshold = 0, variants = None):
        self.text      = text
        self.threshold = threshold
        if variants: self.__variants = [v for v in variants if v.score > threshold]

    @property
    def variants(self):
        if self.__variants is None:
            self.__variants = [v for v in self.__morph.parse(self.text) if v.score > self.threshold]
        return self.__variants

    def __repr__(self):
        if len(self.variants) == 1: return self.text
        else: return self.text + '×' + str(len(self.variants))

    def __eq__(self, other):
        if not isinstance(other, Word): return False
        return self.variants == other.variants

    # Вернуть копию слова, содержащую только подмножество вариантов, содержащих указанную граммему.
    # Возвращает None, если вариантов нет.
    def constrain(self, grammeme):
        if grammeme == ANY: return self
        variants = [variant for variant in self.variants if grammeme in variant.tag.grammemes]
        if not len(variants): return None
        return Word(self.text, variants = variants)

    # Возвращает копию слова с подмножеством вариантов, имеющих указанную нормальную форму.
    # Возвращает None, если вариантов нет.
    def constrain_normal_form(self, normal_form):
        variants = []
        for variant in self.variants:
            if variant.normal_form == normal_form:
                variants.append(variant)
        if not len(variants): return None
        return Word(self.text, variants = variants)

    # Склоняет слово по заданным граммемам
    # По умолчанию фиксирует часть речи (не склоняет "делать" на "делающего", как pymorphy2).
    def inflect(self, grammemes):
        variants = []
        for variant in self.variants:
            inflected = variant.inflect(grammemes)
            if inflected: variants.append(inflected)
        if not len(variants): return None

        own_poss = {g for v in self.variants for g in v.tag.grammemes if g in ABSTRACT_GRAMMEMES[POS]}
        new_poss = {g for v in variants for g in v.tag.grammemes if g in ABSTRACT_GRAMMEMES[POS]}
        poss = own_poss & new_poss
        if not len(poss): return None
        pos = poss.pop()
        variants = [v for v in variants if pos in v.tag.grammemes]
        if not len(variants): return None

        text = variants[0].word
        return Word(text, variants = [v for v in variants if v.word == text])
