import pymorphy2
from .constants import ANY


# Слово представляет строку + набор вариантов его интерпретации с помощью pymorphy2.MorphAnalyzer.
class Word:
    __morph = pymorphy2.MorphAnalyzer()
    __variants = None

    def __init__(self, text, variants = None):
        self.text = text
        if variants: self.__variants = variants

    @property
    def variants(self):
        if self.__variants is None: self.__variants = self.__morph.parse(self.text)
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
        return Word(self.text, variants)
