from unittest import main, TestCase, skip
from polymorphy import Word


class TestWord(TestCase):
    def test(self):
        word = Word('зеленый')
        self.assertEqual(len(word.variants), 2)
        self.assertEqual(word.__repr__(), 'зеленый×2')
        self.assertEqual(word.variants[0].normal_form, 'зелёный')


if __name__ == '__main__':
    unittest.main()
