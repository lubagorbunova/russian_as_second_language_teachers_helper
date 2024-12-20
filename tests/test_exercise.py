import unittest
from src.exercise import SentProcessor, Exercise
from src.files import NothingToWriteError


class ExerciseBaseTests(unittest.TestCase):

    def test_generate_scrambled_sentence_none(self):
        sents = []
        sent = SentProcessor('Кошка спит.')
        sent.process_text()
        sents.append(sent)
        instance = Exercise(sents)
        res = instance.generate_scrambled_sentence()
        self.assertIsNotNone(res)

    def test_generate_scrambled_sentence(self):
        sents = []
        sent = SentProcessor('Кошка спит.')
        sent.process_text()
        sents.append(sent)
        ex = Exercise(sents)
        res = ex.generate_scrambled_sentence()
        try:
            self.assertEqual(res, '\nЗадание №1. Составьте предложение из слов и поставьте их в правильную форму:\nспать, кошка\n\nОтветы на задание 1:\nКошка спит.\n')
        except:
            self.assertEqual(res, '\nЗадание №1. Составьте предложение из слов и поставьте их в правильную форму:\nкошка, спать\n\nОтветы на задание 1:\nКошка спит.\n')

    def test_generate_case_exercise(self):
        sents = []
        sent = SentProcessor('Кошка спит.')
        sent.process_text()
        sents.append(sent)
        ex = Exercise(sents)
        res = ex.generate_case_exercise()

        self.assertEqual(res,
                         f"\nЗадание №2. Выберите правильный падеж для слова:\n'КОШКА' в предложении 'Кошка спит.':\n1. Именительный\n2. Родительный\n3. Дательный\n4. Винительный\n5. Творительный\n6. Предложный\n\n\nОтветы на задание 2:\nИменительный\n")

    def test_generate_case_exercise_not_none(self):
        sent = SentProcessor('Кошка спит')
        sent.process_text()
        sents = []
        sents.append(sent)
        instance = Exercise(sents, number_of_sent_in_each_ex=1)
        res = instance.generate_case_exercise()
        self.assertIsNotNone(res)

    def test_select_grammatical_form_correct_input(self):
        sents = []
        sent = SentProcessor('Кошка спит.')
        sent.process_text()
        sents.append(sent)
        ex = Exercise(sents)
        res = ex.select_grammatical_form(1)
        self.assertEqual(res, '\nЗадание №3. Поставьте слово в скобках в правильную форму:\n_____ [кошка] _____ [спать].\n\n\nОтветы на задание 3:\nКошка спит.\n\n')

    def test_select_grammatical_form_empty_input(self):
        sents = []
        sent = SentProcessor('')
        sent.process_text()
        sents.append(sent)
        ex = Exercise(sents)
        res = ex.select_grammatical_form(1)
        self.assertEqual(res, '\nЗадание №3. Поставьте слово в скобках в правильную форму:\n\n\n\nОтветы на задание 3:\n\n\n')

    def test_select_grammatical_form_no_nouns_or_verbs(self):
        sents = []
        sent = SentProcessor('И где опять?')
        sent.process_text()
        sents.append(sent)
        ex = Exercise(sents)
        res = ex.select_grammatical_form(1)
        self.assertEqual(res, '\nЗадание №3. Поставьте слово в скобках в правильную форму:\nИ где опять?\n\n\nОтветы на задание 3:\nИ где опять?\n\n')

    def test_find_collocations(self):
        sents = []
        sent = SentProcessor('Кошка спит.')
        sent.process_text()
        sents.append(sent)
        ex = Exercise(sents)
        res = ex.find_collocations(1)
        self.assertEqual(res, '\nЗадание №4. Выберите одно или несколько слов из списка, которые подходят в предложение по смыслу.\nПоставьте слово в правильную форму:\n_____[девочка, животное, кошка, птица, рыба, собака] спит.\n\n\nОтветы на задание 4:\n\nКошка спит.\n')

    def test_find_collocations_no_nouns(self):
        sents = []
        sent = SentProcessor('Крепко спит.')
        sent.process_text()
        sents.append(sent)
        ex = Exercise(sents)
        res = ex.find_collocations(1)
        self.assertEqual(res, '\nЗадание №4. Выберите одно или несколько слов из списка, которые подходят в предложение по смыслу.\nПоставьте слово в правильную форму:\nКрепко спит.\n\n\nОтветы на задание 4:\n\nКрепко спит.\n')

