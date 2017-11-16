import os
from lark import Lark, Transformer
from .patterns import *


with open(os.path.dirname(__file__) + '/dsl.ebnf', 'r') as file:
    grammar = file.read()

parser = Lark(grammar, start = 'pattern')


class DSLTransformer(Transformer):
    def pattern_unit(self, items):
        grammeme = items[0].value
        return PatternUnit(grammeme)

    def pattern_word(self, items):
        word = items[0].value[1:-1]
        return PatternWord(word)

    def pattern_lexeme(self, items):
        word = items[0].value[1:-1]
        return PatternLexeme(word)

    def pattern_any(self, items):
        nested = items[0][1]
        return PatternAny(*nested)

    def pattern_all(self, items):
        nested = items[0][1]
        return PatternAll(*nested)

    def pattern_seq(self, items):
        nested = items[0][1]
        return PatternSeq(*nested)

    def pattern_repeat(self, items):
        params = dict(items)
        r_min  = params['r_min'] if 'r_min' in params else 0
        r_max  = params['r_max'] if 'r_max' in params else None
        nested = params['nested_pattern'][0]
        return PatternRepeat(nested, min = r_min, max = r_max)

    def pattern_maybe(self, items):
        nested = items[0][1][0]
        return PatternMaybe(nested)

    def pattern_same(self, items):
        grms   = [token.value for token in items[:-1]]
        nested = items[-1][1][0]
        return PatternSame(grms, nested)

    def pattern_named(self, items):
        name   = items[0].value
        nested = items[-1][1][0]
        return PatternNamed(name, nested)

    def nested_patterns(self, items):
        return ('nested_patterns', items)

    def nested_pattern(self, items):
        return ('nested_pattern', items)

    def r_max(self, items):
        return ('r_max', int(items[0].value))

    def r_min(self, items):
        return ('r_min', int(items[0].value))


transformer = DSLTransformer()


def pattern(text):
    tree    = parser.parse(text)
    return transformer.transform(tree)