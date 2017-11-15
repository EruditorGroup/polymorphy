from unittest import main, TestCase, skip
from polymorphy import Seq
from polymorphy.constants import *
from polymorphy.patterns import *


class TestMatch(TestCase):
    def test_merge_groups(self):
        gs1 = {'foo': [Seq('бежать')], 'baz': [], 'qux': [Seq('стол')]}
        gs2 = {'foo': [Seq('одеяло')], 'bar': [Seq('наверное')]}
        gs3 = Match.merge_groups(gs1, gs2)
        self.assertEqual(gs3, {
            'foo': [Seq('бежать'), Seq('одеяло')],
            'baz': [],
            'qux': [Seq('стол')],
            'bar': [Seq('наверное')],
        })
        self.assertTrue(gs3['qux'] is gs1['qux'])
        self.assertTrue(gs3['bar'] is gs2['bar'])

    def test_add(self):
        m1 = Match(Seq('бежать'), {'foo': ['а']})
        m2 = Match(Seq('одеяло'), {'bar': ['и']})
        m3 = m1 + m2
        self.assertEqual(m3.seq, m1.seq + m2.seq)
        self.assertEqual(m3.groups, Match.merge_groups(m1.groups, m2.groups))

    def test_repr(self):
        m = Match(Seq('бежать'), {'foo': [Seq('а'), Seq('и')], 'bar': [Seq('в')]})
        self.assertEqual(m.__repr__(), 'Match(бежать×2 / 3g)')


class TestPatternUnit(TestCase):
    def test_match(self):
        pattern = PatternUnit(INFN)
        seq     = Seq('бежать одеяло наверное')
        matches = list(pattern.match_gen(seq))
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].seq.text, 'бежать')

    def test_mismatch(self):
        pattern = PatternUnit(NOUN)
        seq     = Seq('бежать одеяло наверное')
        self.assertEqual(len(list(pattern.match_gen(seq))), 0)

    def test_match_any(self):
        pattern = PatternUnit(ANY)
        seq     = Seq('бежать одеяло наверное')
        matches = list(pattern.match_gen(seq))
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].seq.text, 'бежать')


class TestPatternWord(TestCase):
    def test_match(self):
        pattern = PatternWord('столы')
        seq     = Seq('столы большие')
        matches = list(pattern.match_gen(seq))
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].seq.text, 'столы')
        self.assertEqual(matches[0].seq[0], seq[0])

    def test_mismatch(self):
        pattern = PatternWord('стол')
        seq     = Seq('столы большие')
        self.assertEqual(len(list(pattern.match_gen(seq))), 0)


class TestPatternLexeme(TestCase):
    def test_match(self):
        pattern = PatternLexeme('стол')
        seq     = Seq('столы большие')
        matches = list(pattern.match_gen(seq))
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].seq.text, 'столы')

    def test_mismatch(self):
        pattern = PatternLexeme('стул')
        seq     = Seq('столы большие')
        self.assertEqual(len(list(pattern.match_gen(seq))), 0)


class TestPatternAny(TestCase):
    def test_match(self):
        pattern = PatternAny(ADJF, accs)
        seq     = Seq('ведущий')
        self.assertFalse(all(ADJF in v.tag for v in seq.words[0].variants))
        self.assertFalse(all(accs in v.tag for v in seq.words[0].variants))
        matches = list(pattern.match_gen(seq))
        self.assertEqual(len(matches), 2)
        self.assertTrue(all(ADJF in v.tag for v in matches[0].seq.words[0].variants))
        self.assertTrue(all(accs in v.tag for v in matches[1].seq.words[0].variants))

    def test_mismatch(self):
        pattern = PatternAny(ADJF, VERB)
        seq     = Seq('стол бежать')
        self.assertEqual(len(list(pattern.match_gen(seq))), 0)


class TestPatternAll(TestCase):
    def test_match(self):
        pattern = PatternAll(ADJF, accs)
        seq     = Seq('ведущий')
        self.assertFalse(all(accs in variant.tag.grammemes for variant in seq.words[0].variants))
        self.assertFalse(all(ADJF in variant.tag.grammemes for variant in seq.words[0].variants))
        matches = list(pattern.match_gen(seq))
        self.assertEqual(len(matches), 1)
        for variant in matches[0].seq.words[0].variants:
            self.assertTrue(accs in variant.tag.grammemes)
            self.assertTrue(ADJF in variant.tag.grammemes)

    def test_mismatch(self):
        pattern = PatternAll(ADJF, PRTF)
        seq     = Seq('ведущий')
        self.assertEqual(len(list(pattern.match_gen(seq))), 0)


class TestPatternRepeat(TestCase):
    def test_match(self):
        seq     = Seq('большая круглая перламутровая пуговица')
        pattern = PatternRepeat(ADJF)
        matches = list(pattern.match_gen(seq))
        texts   = [match.seq.text for match in matches]
        self.assertEqual(texts, [
            'большая круглая перламутровая',
            'большая круглая',
            'большая',
            '',
        ])

    def test_match_zero(self):
        seq     = Seq('большая круглая перламутровая пуговица')
        pattern = PatternRepeat(INFN)
        matches = list(pattern.match_gen(seq))
        texts   = [match.seq.text for match in matches]
        self.assertEqual(texts, [
            '',
        ])

    def test_match_max(self):
        seq     = Seq('большая круглая перламутровая пуговица')
        pattern = PatternRepeat(ADJF)[:2]
        matches = list(pattern.match_gen(seq))
        texts   = [match.seq.text for match in matches]
        self.assertEqual(texts, [
            'большая круглая',
            'большая',
            '',
        ])

    def test_match_min(self):
        seq     = Seq('большая круглая перламутровая пуговица')
        pattern = PatternRepeat(ADJF)[1:]
        matches = list(pattern.match_gen(seq))
        texts   = [match.seq.text for match in matches]
        self.assertEqual(texts, [
            'большая круглая перламутровая',
            'большая круглая',
            'большая',
        ])

    def test_mismatch(self):
        seq     = Seq('большая круглая перламутровая пуговица')
        pattern = PatternRepeat(INFN)[1:]
        matches = list(pattern.match_gen(seq))
        self.assertEqual(matches, [])


class TestPatternMaybe(TestCase):
    def test_match(self):
        seq     = Seq('большая круглая перламутровая пуговица')
        pattern = PatternMaybe(ADJF)
        matches = list(pattern.match_gen(seq))
        texts   = [match.seq.text for match in matches]
        self.assertEqual(pattern.min_repeats, 0)
        self.assertEqual(pattern.max_repeats, 1)
        self.assertEqual(texts, ['большая', ''])


class TestPatternSeq(TestCase):
    def test_match(self):
        pattern = PatternSeq(NOUN, INFN)
        seq     = Seq('дерево бежать одеяло')
        matches = list(pattern.match_gen(seq))
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].seq.text, 'дерево бежать')

    def test_mismatch(self):
        pattern = PatternSeq(NOUN, INFN)
        seq     = Seq('голова дерево бежать одеяло')
        self.assertEqual(len(list(pattern.match_gen(seq))), 0)


class TestPatternSame(TestCase):
    def test_constrain_same(self):
        seq = Seq('зеленый большой пуговица')

        pattern = PatternSame([CAse], PatternRepeat(ADJF))
        pairs   = []
        for c in pattern.constrain_same(seq):
            grms = {grm for word in c \
                for var in word.variants \
                for grm in var.tag.grammemes \
                if grm in ABSTRACT_GRAMMEMES[CAse]}
            pairs.append((c.text, grms))
        self.assertEqual(pairs, [
            ('зеленый большой пуговица', {'nomn'}),
            ('зеленый большой', {'accs'}),
            ('', set()),
        ])

        pattern = PatternSame([CAse, GNdr], PatternRepeat(ADJF))
        pairs   = []
        for c in pattern.constrain_same(seq):
            grms = {grm for word in c \
                for var in word.variants \
                for grm in var.tag.grammemes \
                if grm in ABSTRACT_GRAMMEMES[CAse] or grm in ABSTRACT_GRAMMEMES[GNdr]}
            pairs.append((c.text, grms))
        self.assertEqual(pairs, [
            ('зеленый большой', {'nomn', 'masc'}), # nomn
            ('зеленый большой', {'accs', 'masc'}), # accs
            ('', set()),
        ])

    def test_match(self):
        pattern = PatternSame([CAse], PatternSeq(ADJF, NOUN))
        seq     = Seq('зеленый стол в углу')
        matches = list(pattern.match_gen(seq))
        texts   = [match.seq.text for match in matches]
        self.assertEqual(texts, [
            'зеленый стол', # nomn
            'зеленый стол', # accs
        ])

    def test_mismatch(self):
        pattern = PatternSame([GNdr], PatternSeq(ADJF, NOUN))
        seq     = Seq('зеленая стол')
        self.assertEqual(len(list(pattern.match_gen(seq))), 0)


class TestComplex(TestCase):
    def test_same_repeat(self):
        pattern = PatternSame([GNdr], PatternRepeat(ANY))
        seq     = Seq('большая зеленая деревянное круглая')
        texts   = [match.seq.text for match in pattern.match_gen(seq)]
        self.assertEqual(texts, ['большая зеленая', 'большая', '', ''])

    def test_seqence_any(self):
        pattern = PatternSeq(ADJF, PatternAny(NOUN, INFN))
        seq1    = Seq('зеленый делать стол')
        seq2    = Seq('зеленый стол делать')
        seq3    = Seq('стол зеленый делать')
        match1  = pattern.match(seq1)
        match2  = pattern.match(seq2)
        text1   = [match.seq.text for match in pattern.match_gen(seq1)]
        text2   = [match.seq.text for match in pattern.match_gen(seq2)]
        self.assertEqual(match1.seq.text, 'зеленый делать')
        self.assertEqual(match2.seq.text, 'зеленый стол')
        self.assertEqual(pattern.match(seq3), None)

    def test_sequence_repeat(self):
        pattern = PatternSeq(ADJF, PatternRepeat(PatternAny(NOUN, INFN))[:2])
        seq1    = Seq('зеленый делать стоять бежать')
        seq2    = Seq('зеленый стол делать')
        seq3    = Seq('зеленый')
        seq4    = Seq('стол зеленый делать стоять')
        texts1  = [match.seq.text for match in pattern.match_gen(seq1)]
        texts2  = [match.seq.text for match in pattern.match_gen(seq2)]
        texts3  = [match.seq.text for match in pattern.match_gen(seq3)]
        texts4  = [match.seq.text for match in pattern.match_gen(seq4)]
        self.assertEqual(texts1, ['зеленый делать стоять', 'зеленый делать', 'зеленый'])
        self.assertEqual(texts2, ['зеленый стол делать', 'зеленый стол', 'зеленый'])
        self.assertEqual(texts3, ['зеленый'])
        self.assertEqual(texts4, [])

    def test_repeat_any(self):
        seq     = Seq('большой стол')
        pattern = PatternRepeat(PatternAny(nomn, accs))
        matches = list(pattern.match_gen(seq))
        texts   = [match.seq.text for match in matches]
        self.assertEqual(texts, [
            'большой стол', # nomn nomn
            'большой стол', # nomn accs
            'большой',      # nomn
            'большой стол', # accs nomn
            'большой стол', # accs accs
            'большой',      # accs
            '',
        ])

    def test_seq_repeat_seq(self):
        seq = Seq('тихий скрип гладкой медной ручки входной двери')
        pattern = PatternSeq(
            PatternSame([GNdr, nomn], PatternSeq(PatternRepeat(ADJF), NOUN)),
            PatternRepeat(
                PatternSame([GNdr, gent], PatternSeq(PatternRepeat(ADJF), NOUN))
            ),
        )
        matches = list(pattern.match_gen(seq))
        texts   = [match.seq.text for match in matches]
        self.assertEqual(texts, [
            'тихий скрип гладкой медной ручки входной двери',
            'тихий скрип гладкой медной ручки',
            'тихий скрип',
        ])


class TestNamed(TestCase):
    def test_simple(self):
        seq     = Seq('тихий скрип медной ручки')
        pattern = PatternNamed('foo', PatternSeq(ADJF, NOUN))
        match   = pattern.match(seq)
        self.assertEqual(len(match.groups), 1)
        self.assertEqual(len(match.groups['foo']), 1)
        self.assertEqual(match.groups['foo'][0].text, 'тихий скрип')

    def test_offset(self):
        seq = Seq('тихий скрип медной ручки входной двери')
        pattern = pattern = PatternSeq(
            PatternSame([GNdr, nomn], PatternSeq(PatternRepeat(ADJF), NOUN)),
            PatternRepeat(PatternNamed('obj',
                PatternSame([GNdr, gent], PatternSeq(PatternRepeat(ADJF), NOUN))
            )),
        )
        matches = list(pattern.match_gen(seq))
        groups_texts = []
        for match in matches:
            groups_texts.append({n: [s.text for s in g] for n, g in match.groups.items()})
        self.assertEqual(groups_texts, [
            {'obj': ['медной ручки', 'входной двери']},
            {'obj': ['медной ручки']},
            {}
        ])

    def test_double(self):
        seq = Seq('тихий скрип медной ручки входной двери')
        pattern = pattern = PatternSeq(
            PatternNamed('act', PatternSame([GNdr, nomn], PatternSeq(PatternRepeat(ADJF), NOUN))),
            PatternRepeat(PatternNamed('obj',
                PatternSame([GNdr, gent], PatternSeq(PatternRepeat(ADJF), NOUN))
            )),
        )
        matches = list(pattern.match_gen(seq))
        groups_texts = []
        for match in matches:
            groups_texts.append({n: [s.text for s in g] for n, g in match.groups.items()})
        self.assertEqual(groups_texts, [
            {'act': ['тихий скрип'], 'obj': ['медной ручки', 'входной двери']},
            {'act': ['тихий скрип'], 'obj': ['медной ручки']},
            {'act': ['тихий скрип']},
        ])


if __name__ == '__main__':
    unittest.main()
