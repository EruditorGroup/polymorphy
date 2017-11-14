from unittest import main, TestCase, skip
from polymorphy import Seq
from polymorphy.constants import ABSTRACT_GRAMMEMES
from polymorphy.constants import ANY, CAse, GNdr, NOUN, ADJF, INFN, VERB, PRTF, nomn, gent, accs, sing, plur, femn
from polymorphy.patterns import PatternUnit, PatternWord, PatternLexem, PatternAny, PatternAll, PatternRepeat, PatternSeq, PatternSame


class TestPatternUnit(TestCase):
    def test_match(self):
        pattern = PatternUnit(INFN)
        seq     = Seq('бежать одеяло наверное')
        matches = list(pattern.match_gen(seq))
        self.assertEqual(len(matches), 1)

        found, remains = matches[0]
        self.assertEqual(found.text, 'бежать')
        self.assertEqual(remains.text, 'одеяло наверное')

    def test_mismatch(self):
        pattern = PatternUnit(NOUN)
        seq     = Seq('бежать одеяло наверное')
        self.assertEqual(len(list(pattern.match_gen(seq))), 0)

    def test_match_any(self):
        pattern = PatternUnit(ANY)
        seq     = Seq('бежать одеяло наверное')
        matches = list(pattern.match_gen(seq))
        self.assertEqual(len(matches), 1)
        found, remains = matches[0]
        self.assertEqual(found.text, 'бежать')
        self.assertEqual(remains.text, 'одеяло наверное')


class TestPatternWord(TestCase):
    def test_match(self):
        pattern = PatternWord('столы')
        seq = Seq('столы большие')
        matches = list(pattern.match_gen(seq))
        self.assertEqual(len(matches), 1)
        found, remains = matches[0]
        self.assertEqual(found.text, 'столы')
        self.assertEqual(remains.text, 'большие')
        self.assertEqual(found[0], seq[0])

    def test_mismatch(self):
        pattern = PatternWord('стол')
        seq = Seq('столы большие')
        self.assertEqual(len(list(pattern.match_gen(seq))), 0)


class TestPatternLexem(TestCase):
    def test_match(self):
        pattern = PatternLexem('стол')
        seq = Seq('столы большие')
        matches = list(pattern.match_gen(seq))
        self.assertEqual(len(matches), 1)
        found, remains = matches[0]
        self.assertEqual(found.text, 'столы')
        self.assertEqual(remains.text, 'большие')

    def test_mismatch(self):
        pattern = PatternLexem('стул')
        seq = Seq('столы большие')
        self.assertEqual(len(list(pattern.match_gen(seq))), 0)


class TestPatternAny(TestCase):
    def test_match(self):
        pattern = PatternAny(ADJF, accs)
        seq     = Seq('ведущий')
        self.assertFalse(all(ADJF in v.tag for v in seq.words[0].variants))
        self.assertFalse(all(accs in v.tag for v in seq.words[0].variants))
        matches = list(pattern.match_gen(seq))
        self.assertEqual(len(matches), 2)
        self.assertTrue(all(ADJF in v.tag for v in matches[0][0].words[0].variants))
        self.assertTrue(all(accs in v.tag for v in matches[1][0].words[0].variants))

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
        for found, remains in matches:
            self.assertEqual(remains, Seq())
            for variant in found.words[0].variants:
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
        texts   = [(found.text, remains.text) for found, remains in matches]
        self.assertEqual(texts, [
            ('большая круглая перламутровая', 'пуговица'),
            ('большая круглая', 'перламутровая пуговица'),
            ('большая', 'круглая перламутровая пуговица'),
            ('', 'большая круглая перламутровая пуговица'),
        ])

    def test_match_zero(self):
        seq     = Seq('большая круглая перламутровая пуговица')
        pattern = PatternRepeat(INFN)
        matches = list(pattern.match_gen(seq))
        texts   = [(found.text, remains.text) for found, remains in matches]
        self.assertEqual(texts, [
            ('', 'большая круглая перламутровая пуговица'),
        ])

    def test_match_max(self):
        seq     = Seq('большая круглая перламутровая пуговица')
        pattern = PatternRepeat(ADJF)[:2]
        matches = list(pattern.match_gen(seq))
        texts   = [(found.text, remains.text) for found, remains in matches]
        self.assertEqual(texts, [
            ('большая круглая', 'перламутровая пуговица'),
            ('большая', 'круглая перламутровая пуговица'),
            ('', 'большая круглая перламутровая пуговица'),
        ])

    def test_match_min(self):
        seq     = Seq('большая круглая перламутровая пуговица')
        pattern = PatternRepeat(ADJF)[1:]
        matches = list(pattern.match_gen(seq))
        texts   = [(found.text, remains.text) for found, remains in matches]
        self.assertEqual(texts, [
            ('большая круглая перламутровая', 'пуговица'),
            ('большая круглая', 'перламутровая пуговица'),
            ('большая', 'круглая перламутровая пуговица'),
        ])

    def test_mismatch(self):
        seq     = Seq('большая круглая перламутровая пуговица')
        pattern = PatternRepeat(INFN)[1:]
        matches = list(pattern.match_gen(seq))
        self.assertEqual(matches, [])


class TestPatternSeq(TestCase):
    def test_match(self):
        pattern = PatternSeq(NOUN, INFN)
        seq     = Seq('дерево бежать одеяло')
        matches = list(pattern.match_gen(seq))
        self.assertEqual(len(matches), 1)
        found, remains = matches[0]
        self.assertEqual(found.text, 'дерево бежать')
        self.assertEqual(remains.text, 'одеяло')

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
        texts   = [(found.text, remains.text) for found, remains in matches]
        self.assertEqual(texts, [
            ('зеленый стол', 'в углу'), # nomn
            ('зеленый стол', 'в углу'), # accs
        ])

    def test_mismatch(self):
        pattern = PatternSame([GNdr], PatternSeq(ADJF, NOUN))
        seq     = Seq('зеленая стол')
        self.assertEqual(len(list(pattern.match_gen(seq))), 0)


class TestComplex(TestCase):
    def test_same_repeat(self):
        pattern = PatternSame([GNdr], PatternRepeat(ANY))
        seq     = Seq('большая зеленая деревянное круглая')
        found, remains = pattern.match(seq)
        self.assertEqual(found.text, 'большая зеленая')
        self.assertEqual(remains.text, 'деревянное круглая')

    def test_seqence_any(self):
        pattern = PatternSeq(ADJF, PatternAny(NOUN, INFN))
        seq1    = Seq('зеленый делать стол')
        seq2    = Seq('зеленый стол делать')
        seq3    = Seq('стол зеленый делать')
        found1, remains1 = pattern.match(seq1)
        found2, remains2 = pattern.match(seq2)
        self.assertEqual(found1.text, 'зеленый делать')
        self.assertEqual(found2.text, 'зеленый стол')
        self.assertEqual(remains1.text, 'стол')
        self.assertEqual(remains2.text, 'делать')
        self.assertEqual(pattern.match(seq3), None)

    def test_sequence_repeat(self):
        pattern = PatternSeq(ADJF, PatternRepeat(PatternAny(NOUN, INFN))[:2])
        seq1 = Seq('зеленый делать стоять бежать')
        seq2 = Seq('зеленый стол делать')
        seq3 = Seq('зеленый')
        seq4 = Seq('стол зеленый делать стоять')
        found1, remains1 = pattern.match(seq1)
        found2, remains2 = pattern.match(seq2)
        found3, remains3 = pattern.match(seq3)
        self.assertEqual(found1.text, 'зеленый делать стоять')
        self.assertEqual(found2.text, 'зеленый стол делать')
        self.assertEqual(found3.text, 'зеленый')
        self.assertEqual(remains1.text, 'бежать')
        self.assertEqual(remains2.text, '')
        self.assertEqual(remains3.text, '')
        self.assertEqual(pattern.match(seq4), None)

    def test_repeat_any(self):
        seq     = Seq('большой стол')
        pattern = PatternRepeat(PatternAny(nomn, accs))
        matches = list(pattern.match_gen(seq))
        texts   = [(found.text, remains.text) for found, remains in matches]
        self.assertEqual(texts, [
            ('большой стол', ''), # nomn nomn
            ('большой стол', ''), # nomn accs
            ('большой', 'стол'),  # nomn
            ('большой стол', ''), # accs nomn
            ('большой стол', ''), # accs accs
            ('большой', 'стол'),  # accs
            ('', 'большой стол'),
        ])

    def test_repeat_seq(self):
        seq = Seq('тихий скрип гладкой медной ручки входной двери')
        pattern = PatternSeq(
            PatternSame([GNdr, nomn], PatternSeq(PatternRepeat(ADJF), NOUN)),
            PatternRepeat(
                PatternSame([GNdr, gent], PatternSeq(PatternRepeat(ADJF), NOUN))
            ),
        )
        matches = list(pattern.match_gen(seq))
        found   = [found.text for found, remains in matches]
        self.assertEqual(found, [
            'тихий скрип гладкой медной ручки входной двери',
            'тихий скрип гладкой медной ручки',
            'тихий скрип',
        ])


if __name__ == '__main__':
    unittest.main()
