from unittest import main, TestCase, skip
from lark import Tree
from lark.lexer import Token
from polymorphy import Seq
from polymorphy.constants import *
from polymorphy.patterns import *
from polymorphy.dsl import *


def simplify_tree(tree):
    if isinstance(tree, Tree):
        return {tree.data: [simplify_tree(child) for child in tree.children]}
    else:
        return tree.value


class TestParser(TestCase):
    def test_pattern_unit(self):
        tree = simplify_tree(parser.parse('POS'))
        self.assertEqual(tree, {'root': [{'pattern_unit': ['POS']}]})

        tree = simplify_tree(parser.parse('nomn'))
        self.assertEqual(tree, {'root': [{'pattern_unit': ['nomn']}]})

    def test_pattern_word(self):
        tree = simplify_tree(parser.parse('word("привет")'))
        self.assertEqual(tree, {'root': [{'pattern_word': ['"привет"']}]})

    def test_pattern_lexeme(self):
        tree = simplify_tree(parser.parse('lexeme("привет")'))
        self.assertEqual(tree, {'root': [{'pattern_lexeme': ['"привет"']}]})

    def test_pattern_any(self):
        tree = simplify_tree(parser.parse('any { ADJF gent }'))
        self.assertEqual(tree, {'root': [{'pattern_any': [{'nested_patterns': [
            {'pattern_unit': ['ADJF']},
            {'pattern_unit': ['gent']},
        ]}]}]})

    def test_pattern_all(self):
        tree = simplify_tree(parser.parse('all { ADJF gent }'))
        self.assertEqual(tree, {'root': [{'pattern_all': [{'nested_patterns': [
            {'pattern_unit': ['ADJF']},
            {'pattern_unit': ['gent']},
        ]}]}]})

    def test_pattern_seq(self):
        tree = simplify_tree(parser.parse('seq { NOUN ADJF }'))
        self.assertEqual(tree, {'root': [{'pattern_seq': [{'nested_patterns': [
            {'pattern_unit': ['NOUN']},
            {'pattern_unit': ['ADJF']},
        ]}]}]})

    def test_pattern_repeat(self):
        tree = simplify_tree(parser.parse('repeat { NOUN }'))
        self.assertEqual(tree, {'root': [{'pattern_repeat': [{'nested_pattern': [
            {'pattern_unit': ['NOUN']},
        ]}]}]})

        tree = simplify_tree(parser.parse('repeat(3:) { NOUN }'))
        self.assertEqual(tree, {'root': [{'pattern_repeat': [
            {'r_min': ['3']},
            {'nested_pattern': [{'pattern_unit': ['NOUN']}]},
        ]}]})

        tree = simplify_tree(parser.parse('repeat(:4) { NOUN }'))
        self.assertEqual(tree, {'root': [{'pattern_repeat': [
            {'r_max': ['4']},
            {'nested_pattern': [
                {'pattern_unit': ['NOUN']},
            ]}
        ]}]})

        tree = simplify_tree(parser.parse('repeat(3:4) { NOUN }'))
        self.assertEqual(tree, {'root': [{'pattern_repeat': [
            {'r_min': ['3']},
            {'r_max': ['4']},
            {'nested_pattern': [
                {'pattern_unit': ['NOUN']},
            ]}
        ]}]})

    def test_pattern_maybe(self):
        tree = simplify_tree(parser.parse('maybe { NOUN }'))
        self.assertEqual(tree, {'root': [{'pattern_maybe': [{'nested_pattern': [
            {'pattern_unit': ['NOUN']},
        ]}]}]})

    def test_pattern_same(self):
        tree = simplify_tree(parser.parse('same(GNdr CAse) { seq { NOUN ADJF } }'))
        self.assertEqual(tree, {'root': [{'pattern_same': [
            'GNdr',
            'CAse',
            {'nested_pattern': [
                {'pattern_seq': [{'nested_patterns': [
                    {'pattern_unit': ['NOUN']},
                    {'pattern_unit': ['ADJF']},
                ]}]},
            ]},
        ]}]})

    def test_pattern_named(self):
        tree = simplify_tree(parser.parse('$foobar: NOUN'))
        self.assertEqual(tree, {'root': [{'pattern_named': [
            'foobar',
            {'pattern_unit': ['NOUN']},
        ]}]})

    def test_fragments(self):
        tree = simplify_tree(parser.parse('seq { @obj @obj } @obj: seq { ADJF NOUN }'))
        self.assertEqual(tree, {'root': [
            {'pattern_seq': [{'nested_patterns': [
                {'fragment_ref': ['obj']},
                {'fragment_ref': ['obj']}
            ]}]},
            {'fragment_def': [
                'obj',
                {'pattern_seq': [{'nested_patterns': [
                    {'pattern_unit': ['ADJF']},
                    {'pattern_unit': ['NOUN']},
                ]}]},
            ]},
        ]})

    def test_whitespaces(self):
        tree1 = simplify_tree(parser.parse('same(GNdr CAse) { seq { ADJF, NOUN, @foo } }, @foo: repeat { ANY }'))
        tree2 = simplify_tree(parser.parse('''
            same(GNdr, CAse) {
                seq {
                    ADJF
                    NOUN
                    @foo
                }
            }
            @foo: repeat {
                ANY
            }
        '''))
        self.assertEqual(tree1, tree2)


class TestTransformer(TestCase):
    def test_pattern_unit(self):
        p = pattern('nomn')
        self.assertTrue(isinstance(p, PatternUnit))
        self.assertEqual(p.grammeme, 'nomn')

    def test_pattern_word(self):
        p = pattern('word("привет")')
        self.assertTrue(isinstance(p, PatternWord))
        self.assertEqual(p.word, 'привет')

    def test_pattern_lexeme(self):
        p = pattern('lexeme("привет")')
        self.assertTrue(isinstance(p, PatternLexeme))
        self.assertEqual(p.normal_form, 'привет')

    def test_pattern_any(self):
        p = pattern('any { ADJF gent }')
        self.assertTrue(isinstance(p, PatternAny))
        self.assertEqual(len(p.patterns), 2)
        self.assertTrue(isinstance(p.patterns[0], PatternUnit))
        self.assertTrue(isinstance(p.patterns[1], PatternUnit))
        self.assertEqual(p.patterns[0].grammeme, 'ADJF')
        self.assertEqual(p.patterns[1].grammeme, 'gent')

    def test_pattern_all(self):
        p = pattern('all { ADJF gent }')
        self.assertTrue(isinstance(p, PatternAll))
        self.assertEqual(len(p.patterns), 2)
        self.assertTrue(isinstance(p.patterns[0], PatternUnit))
        self.assertTrue(isinstance(p.patterns[1], PatternUnit))
        self.assertEqual(p.patterns[0].grammeme, 'ADJF')
        self.assertEqual(p.patterns[1].grammeme, 'gent')

    def test_pattern_seq(self):
        p = pattern('seq { NOUN ADJF }')
        self.assertTrue(isinstance(p, PatternSeq))
        self.assertEqual(len(p.parts), 2)
        self.assertTrue(isinstance(p.parts[0], PatternUnit))
        self.assertTrue(isinstance(p.parts[1], PatternUnit))
        self.assertEqual(p.parts[0].grammeme, 'NOUN')
        self.assertEqual(p.parts[1].grammeme, 'ADJF')

    def test_pattern_repeat(self):
        p = pattern('repeat { NOUN }')
        self.assertTrue(isinstance(p, PatternRepeat))
        self.assertEqual(p.min_repeats, 0)
        self.assertEqual(p.max_repeats, None)
        self.assertTrue(isinstance(p.sub, PatternUnit))
        self.assertEqual(p.sub.grammeme, 'NOUN')

        p = pattern('repeat(3:) { NOUN }')
        self.assertEqual(p.min_repeats, 3)
        self.assertEqual(p.max_repeats, None)

        p = pattern('repeat(:4) { NOUN }')
        self.assertEqual(p.min_repeats, 0)
        self.assertEqual(p.max_repeats, 4)

        p = pattern('repeat(2:5) { NOUN }')
        self.assertEqual(p.min_repeats, 2)
        self.assertEqual(p.max_repeats, 5)

    def test_pattern_maybe(self):
        p = pattern('maybe { NOUN }')
        self.assertTrue(isinstance(p, PatternMaybe))

    def test_pattern_same(self):
        p = pattern('same(GNdr CAse) { seq { NOUN ADJF } }')
        self.assertTrue(isinstance(p, PatternSame))
        self.assertTrue(isinstance(p.sub, PatternSeq))
        self.assertTrue(isinstance(p.sub.parts[0], PatternUnit))
        self.assertTrue(isinstance(p.sub.parts[1], PatternUnit))
        self.assertEqual(p.sub.parts[0].grammeme, 'NOUN')
        self.assertEqual(p.sub.parts[1].grammeme, 'ADJF')

    def test_pattern_named(self):
        p = pattern('$foobar: NOUN')
        self.assertTrue(isinstance(p, PatternNamed))
        self.assertEqual(p.name, 'foobar')
        self.assertTrue(isinstance(p.sub, PatternUnit))
        self.assertEqual(p.sub.grammeme, 'NOUN')


class TestFragments(TestCase):
    def test_fragment(self):
        p = pattern('''
            seq {
                same(nomn) { @obj }
                same(gent) { @obj }
            }

            @obj: same(GNdr) { seq { repeat { ADJF } NOUN } }
        ''')
        self.assertTrue(isinstance(p, PatternSeq))
        self.assertTrue(isinstance(p.parts[0], PatternSame))
        self.assertTrue(isinstance(p.parts[1], PatternSame))
        self.assertEqual(p.parts[0].grms, [[nomn]])
        self.assertEqual(p.parts[1].grms, [[gent]])
        self.assertTrue(p.parts[0].sub is p.parts[1].sub)
        self.assertTrue(isinstance(p.parts[0].sub, PatternSame))
        self.assertEqual(p.parts[0].sub.grms, [ABSTRACT_GRAMMEMES[GNdr]])

    def test_2_fragments(self):
        p = pattern('''
            seq { @obj1 @obj2 }
            @obj1: NOUN
            @obj2: ADJF
        ''')
        self.assertTrue(isinstance(p, PatternSeq))
        self.assertTrue(isinstance(p.parts[0], PatternUnit))
        self.assertTrue(isinstance(p.parts[1], PatternUnit))
        self.assertTrue(p.parts[0].grammeme, NOUN)
        self.assertTrue(p.parts[1].grammeme, ADJF)

    def test_fragments_in_fragments(self):
        p = pattern('''
            repeat { @obj1 }
            @obj1: seq { @obj2, @obj3 }
            @obj2: NOUN
            @obj3: ADJF
        ''')
        self.assertTrue(isinstance(p, PatternRepeat))
        self.assertTrue(isinstance(p.sub, PatternSeq))
        self.assertTrue(isinstance(p.sub.parts[0], PatternUnit))
        self.assertTrue(isinstance(p.sub.parts[0], PatternUnit))
        self.assertEqual(p.sub.parts[0].grammeme, NOUN)
        self.assertEqual(p.sub.parts[1].grammeme, ADJF)

