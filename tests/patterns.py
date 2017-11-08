from unittest import main, TestCase, skip
from polymorphy import Seq
from polymorphy.constants import ANY, CAse, GNdr, NOUN, ADJF, INFN, VERB, nomn, gent, sing, plur, femn
from polymorphy.patterns import PatternUnit, PatternWord, PatternLexem, PatternAny, PatternAll, PatternRepeat, PatternSeq, PatternSame


class TestPatternUnit(TestCase):
    def setUp(self):
        self.seq = Seq('бежать одеяло наверное')

    def test_match(self):
        pattern = PatternUnit(INFN)
        found, remains = pattern.match(self.seq)
        self.assertEqual(found.text, 'бежать')
        self.assertEqual(remains.text, 'одеяло наверное')

    def test_mismatch(self):
        pattern = PatternUnit(NOUN)
        self.assertEqual(pattern.match(self.seq), None)

    def test_match_any(self):
        pattern = PatternUnit(ANY)
        found, remains = pattern.match(self.seq)
        self.assertEqual(found.text, 'бежать')
        self.assertEqual(remains.text, 'одеяло наверное')


class TestPatternWord(TestCase):
    def test_match(self):
        pattern = PatternWord('столы')
        seq = Seq('столы большие')
        found, remains = pattern.match(seq)
        self.assertEqual(found.text, 'столы')
        self.assertEqual(remains.text, 'большие')
        self.assertEqual(found[0], seq[0])

    def test_mismatch(self):
        pattern = PatternWord('стол')
        seq = Seq('столы большие')
        self.assertEqual(pattern.match(seq), None)


class TestPatternLexem(TestCase):
    def test_match(self):
        pattern = PatternLexem('стол')
        seq = Seq('столы большие')
        found, remains = pattern.match(seq)
        self.assertEqual(found.text, 'столы')
        self.assertEqual(remains.text, 'большие')

    def test_mismatch(self):
        pattern = PatternLexem('стул')
        seq = Seq('столы большие')
        self.assertEqual(pattern.match(seq), None)


class TestPatternAny(TestCase):
    def test_match(self):
        pattern = PatternAny(NOUN, gent)
        seq     = Seq('лалала')
        found, remains = pattern.match(seq)
        self.assertFalse(all(NOUN in v.tag for v in seq.words[0].variants))
        self.assertTrue(all(NOUN in v.tag for v in found.words[0].variants))
        self.assertFalse(all(gent in v.tag for v in found.words[0].variants))

    def test_mismatch(self):
        pattern = PatternAny(ADJF, VERB)
        seq     = Seq('стол бежать')
        match   = pattern.match(seq)
        self.assertEqual(match, None)


class TestPatternAll(TestCase):
    def test_match(self):
        pattern = PatternAll(NOUN, nomn)
        seq     = Seq('лалала')
        found, remains = pattern.match(seq)
        self.assertEqual(remains, Seq())
        self.assertFalse(all(nomn in variant.tag.grammemes for variant in seq.words[0].variants))
        self.assertFalse(all(NOUN in variant.tag.grammemes for variant in seq.words[0].variants))
        for variant in found.words[0].variants:
            self.assertTrue(nomn in variant.tag.grammemes)
            self.assertTrue(NOUN in variant.tag.grammemes)

    def test_mismatch(self):
        pattern = PatternAll(nomn, gent)
        seq     = Seq('лалала')
        match = pattern.match(seq)
        self.assertEqual(match, None)


class TestPatternRepeat(TestCase):
    def setUp(self):
        self.seq = Seq('голова стол дерево бежать одеяло')

    def test_match(self):
        pattern = PatternRepeat(NOUN)
        found, remains = pattern.match(self.seq)
        self.assertEqual(found.text, 'голова стол дерево')
        self.assertEqual(remains.text, 'бежать одеяло')

    def test_match_zero(self):
        pattern = PatternRepeat(INFN)
        found, remains = pattern.match(self.seq)
        self.assertEqual(found.text, '')
        self.assertEqual(remains.text, 'голова стол дерево бежать одеяло')

    def test_match_max(self):
        pattern = PatternRepeat(NOUN)[:2]
        found, remains = pattern.match(self.seq)
        self.assertEqual(found.text, 'голова стол')
        self.assertEqual(remains.text, 'дерево бежать одеяло')

    def test_match_min(self):
        seq = Seq('топографической съемки местности')
        found, remains = PatternRepeat(gent)[1:].match(seq)
        self.assertEqual(found.text, seq.text)
        self.assertEqual(len(remains), 0)
        self.assertEqual(PatternRepeat(gent)[4:].match(seq), None)


class TestPattern(TestCase):
    def test_match(self):
        pattern = PatternSeq(NOUN, INFN)
        seq     = Seq('дерево бежать одеяло')
        found, remains = pattern.match(seq)
        self.assertEqual(found.text, 'дерево бежать')
        self.assertEqual(remains.text, 'одеяло')

    def test_mismatch(self):
        pattern = PatternSeq(NOUN, INFN)
        seq     = Seq('голова дерево бежать одеяло')
        match   = pattern.match(seq)
        self.assertEqual(match, None)


class TestPatternSame(TestCase):
    def test_match(self):
        pattern = PatternSame([CAse], PatternSeq(ADJF, NOUN))
        seq     = Seq('зеленый стол большой')
        found, remains = pattern.match(seq)
        self.assertEqual(found.text, 'зеленый стол')
        self.assertEqual(remains.text, 'большой')
        self.assertFalse(all(nomn in v.tag.grammemes for word in seq[:2] for v in word.variants))
        self.assertTrue(all(nomn in v.tag.grammemes for word in found for v in word.variants))

    def test_mismatch(self):
        pattern = PatternSame([GNdr], PatternSeq(ADJF, NOUN))
        seq     = Seq('большой зеленое')
        match   = pattern.match(seq)
        self.assertEqual(match, None)


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


if __name__ == '__main__':
    unittest.main()
