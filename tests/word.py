from unittest import main, TestCase, skip
from polymorphy import Word
from polymorphy.constants import PREP, nomn, accs


class TestWord(TestCase):
    def test(self):
        word = Word('зеленый')
        self.assertEqual(len(word.variants), 2)
        self.assertEqual(word.__repr__(), 'зеленый×2')
        self.assertEqual(word.variants[0].normal_form, 'зелёный')

    def test_threshold(self):
        word1 = Word('в')
        word2 = Word('в', 0.01)
        self.assertFalse(all(PREP in v.tag.grammemes for v in word1.variants))
        self.assertTrue(all(PREP in v.tag.grammemes for v in word2.variants))

    def test_constrain(self):
        word = Word('стол')
        constrained = word.constrain(nomn)
        self.assertEqual(len(word.variants), 2)
        self.assertEqual(len(constrained.variants), 1)
        self.assertTrue(any(accs in v.tag.grammemes for v in word.variants))
        self.assertFalse(any(accs in v.tag.grammemes for v in constrained.variants))

    def test_constrain_nf(self):
        word = Word('лалала')
        constrained = word.constrain_normal_form('лалал')
        self.assertTrue(len(constrained.variants) < len(word.variants))
        self.assertTrue(all(v.normal_form == 'лалал' for v in constrained.variants))
        self.assertTrue(any(v.normal_form != 'лалал' for v in word.variants))


if __name__ == '__main__':
    unittest.main()
