from unittest import main, TestCase, skip
from polymorphy import Word
from polymorphy.constants import nomn, accs


class TestWord(TestCase):
    def test(self):
        word = Word('зеленый')
        self.assertEqual(len(word.variants), 2)
        self.assertEqual(word.__repr__(), 'зеленый×2')
        self.assertEqual(word.variants[0].normal_form, 'зелёный')

    def test_constrain(self):
        word = Word('стол')
        constrained = word.constrain(nomn)
        self.assertEqual(len(word.variants), 2)
        self.assertEqual(len(constrained.variants), 1)
        self.assertTrue(any(accs in v.tag.grammemes for v in word.variants))
        self.assertFalse(any(accs in v.tag.grammemes for v in constrained.variants))


if __name__ == '__main__':
    unittest.main()
