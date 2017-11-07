from unittest import main, TestCase, skip
from polymorphy import Seq


class TestSeq(TestCase):
    def test(self):
        seq = Seq('зеленый перец')
        self.assertEqual(seq.text, 'зеленый перец')
        for word in seq.words:
            self.assertEqual(len(word.variants), 2)

    def test_representation(self):
        seq1 = Seq('зеленый перец')
        seq2 = Seq('не плоховат')
        for word in seq1.words: self.assertEqual(len(word.variants), 2)
        for word in seq2.words: self.assertEqual(len(word.variants), 1)
        self.assertEqual(seq1.__repr__(), 'Seq(зеленый×2 перец×2)')
        self.assertEqual(seq2.__repr__(), 'Seq(не плоховат)')

    def test_empty_seq(self):
        seq = Seq('')
        self.assertEqual(seq.words, [])

    def test_constrain(self):
        seq1 = Seq('зеленый перец')
        seq2 = seq1.constrain('nomn')
        for word in seq1.words: self.assertEqual(len(word.variants), 2)
        for word in seq2.words: self.assertEqual(len(word.variants), 1)

    def test_constrain_any(self):
        seq = Seq('зеленый перец')
        self.assertEqual(seq, seq.constrain('ANY'))


if __name__ == '__main__':
    unittest.main()
