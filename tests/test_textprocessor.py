import unittest
from src.exercise import SentProcessor
import numpy
from pymorphy2.tagset import OpencorporaTag


class SentProcessorBaseTests(unittest.TestCase):

    def test_getrawtext(self):
        sentences = ['Кошка спит на диване', 'Кошка спит', 'кошка,,,,, спит.....']
        for sent in sentences:
            instance = SentProcessor(sent)
            self.assertEqual(instance.get_raw_text(), sent)

    def test_getrawtext_corrupted(self):
        instance = SentProcessor(None)
        self.assertEqual(instance.get_raw_text(), None)

    def test_getrawinput_incorrect_input(self):
        sentences = [123, ('Кошка спит', ), [None]]
        for sent in sentences:
            instance = SentProcessor(sent)
            self.assertEqual(instance.get_raw_text(), None)

    def test_tokenise(self):
        instance = SentProcessor('Кошка спит на диване!')
        instance.process_text()
        self.assertEqual(instance._tokens, ['кошка', 'спит', 'на', 'диване'])

    def test_lemmas(self):
        text = 'Кошка спит на диване!'
        instance = SentProcessor(text)
        instance.process_text()
        expected_lemmas = ['кошка', 'спать', 'на', 'диван']
        self.assertEqual(instance._lemma_text, expected_lemmas)

    def test_lemma_text_empty_after_processing_empty_text(self):
        empty_text = ''
        instance = SentProcessor(empty_text)
        instance.process_text()
        expected_lemmas = []
        self.assertEqual(instance._lemma_text, expected_lemmas)

    def test_get_lemmas_unusual_characters(self):
        text = 'Кошка спит....zzZZzz'
        instance = SentProcessor(text)
        instance.process_text()
        lemmas = instance.get_lemmas()
        expected_lemmas = ['кошка', 'спать', 'zzzzzz']
        self.assertEqual(lemmas, expected_lemmas)

    def test_get_lemmas_no_words(self):
        text = '!@#$%^&*()'
        instance = SentProcessor(text)
        instance.process_text()
        lemmas = instance.get_lemmas()
        expected_lemmas = []
        self.assertEqual(lemmas, expected_lemmas)

    def test_vectorise(self):
        sentences = ['Кошка', 'stjrdvrdjfvkjy']
        for sent in sentences:
            instance = SentProcessor(sent)
            instance.process_text()
            self.assertEqual(type(instance._vector[sent.lower()]), numpy.ndarray)

    def test_vectorise_corrupted_input(self):
        instance = SentProcessor('')
        instance.process_text()
        self.assertEqual(instance._vector, {})

    def test_get_vectors_access_check(self):
        instance = SentProcessor('кошка')
        instance._vector = 0
        self.assertEqual(instance.get_vectors(), 0)

    def test_get_vectors_type_check(self):
        instance = SentProcessor('кошка')
        instance.process_text()
        self.assertEqual(type(instance.get_vectors()['кошка']), numpy.ndarray)
        self.assertEqual(type(instance.get_vectors()), dict)

    def test_process_text_values(self):
        instance = SentProcessor('Кошка спит на диване 0!')
        instance.process_text()
        self.assertEqual(instance._tokens, ['кошка', 'спит', 'на', 'диване', '0'])
        self.assertEqual(instance._lemma_text, ['кошка', 'спать', 'на', 'диван', '0'])
        self.assertEqual(instance._morph, [OpencorporaTag('NOUN,anim,femn sing,nomn'),
                                                OpencorporaTag('VERB,impf,intr sing,3per,pres,indc'),
                                                OpencorporaTag('PREP'),
                                                OpencorporaTag('NOUN,inan,masc sing,loct'),
                                                OpencorporaTag('NUMB,intg')])
        for vector in instance._vector.values():
            self.assertEqual(type(vector), numpy.ndarray)

    def test_process_text_types(self):
        instance = SentProcessor('Кошка спит на диване 0!')
        instance.process_text()
        self.assertEqual(type(instance.get_tokens()[0]), str)
        self.assertEqual(type(instance.get_lemmas()[0]), str)
        self.assertEqual(type(instance.get_morph()[0]), OpencorporaTag)
        self.assertEqual(type(instance.get_vectors()['кошка']), numpy.ndarray)

        self.assertEqual(type(instance.get_tokens()), list)
        self.assertEqual(type(instance.get_lemmas()), list)
        self.assertEqual(type(instance.get_morph()), list)
        self.assertEqual(type(instance.get_vectors()), dict)
