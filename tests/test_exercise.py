import unittest
from src.exercise import SentProcessor, Exercise

import numpy
from pymorphy2.tagset import OpencorporaTag

from src.files import NothingToWriteError
from src.word import Word

class ExerciseBaseTests(unittest.TestCase):

    def test_generate_scrambled_sentence_none(self):
        sents = []
        sent = SentProcessor('Кошка спит.')
        sent.process_text()
        sents.append(sent)
        instance = Exercise(sents)
        instance.generate_scrambled_sentence()
        self.assertIsNotNone(instance.compose_ex)
        self.assertIsNotNone(instance.compose_answers)

    def test_generate_scrambled_sentence(self):
        sents = []
        sent = SentProcessor('Кошка спит.')
        sent.process_text()
        sents.append(sent)
        ex = Exercise(sents)
        ex.generate_scrambled_sentence()
        test_value = False
        if ex.compose_ex == '\nЗадание №3. Составьте предложение из слов и поставьте их в правильную форму:\n[спать], [кошка]\n'\
                or ex.compose_ex == '\nЗадание №3. Составьте предложение из слов и поставьте их в правильную форму:\n[кошка], [спать]\n':
            test_value = True
        self.assertTrue(test_value, 'WRONG OPTIONS')
        self.assertEqual(ex.compose_answers, '\nОтветы на задание №3:\nКошка спит.\n')

    def test_generate_case_exercise(self):
        sents = []
        sent = SentProcessor('Кошка спит.')
        sent.process_text()
        sents.append(sent)
        ex = Exercise(sents)
        ex.generate_case_exercise()

        self.assertEqual(ex.case_ex,
                         f"Задание №4: Выберите правильный падеж для слова 'КОШКА' в предложении 'Кошка спит':\n")

        self.assertEqual(ex.case_answers, f"Правильный ответ: Именительный")

    def test_generate_case_exercise(self):
        sent = SentProcessor('Кошка спит')
        sent.process_text()
        sents = []
        sents.append(sent)
        instance = Exercise(sents, number_of_sent_in_each_ex=1)
        instance.generate_case_exercise()
        self.assertIsNotNone(instance.case_ex)
        self.assertIsNotNone(instance.case_answers)

    def test_select_grammatical_form_correct_input(self):
        sents = []
        sent = SentProcessor('Кошка спит.')
        sent.process_text()
        sents.append(sent)
        ex = Exercise(sents)
        ex.select_grammatical_form(1)
        self.assertEqual(ex.forms_ex, '\nЗадание №5: Поставьте слово в скобках в правильную форму:\n_____ [кошка] _____ [спать].\n')
        self.assertEqual(ex.forms_answers, '\nОтветы на задание №5: \nКошка спит.\n')

    def test_select_grammatical_form_empty_input(self):
        sents = []
        sent = SentProcessor('')
        sent.process_text()
        sents.append(sent)
        ex = Exercise(sents)
        ex.select_grammatical_form(1)
        self.assertEqual(ex.forms_ex, '\nЗадание №5: Поставьте слово в скобках в правильную форму:\n\n')
        self.assertEqual(ex.forms_answers, '\nОтветы на задание №5: \n\n')

    def test_select_grammatical_form_no_nouns_or_verbs(self):
        sents = []
        sent = SentProcessor('И где опять?')
        sent.process_text()
        sents.append(sent)
        ex = Exercise(sents)
        ex.select_grammatical_form(1)
        self.assertEqual(ex.forms_ex, '\nЗадание №5: Поставьте слово в скобках в правильную форму:\nИ где опять?\n')
        self.assertEqual(ex.forms_answers, '\nОтветы на задание №5: \nИ где опять?\n')

    def test_find_collocations(self):
        sents = []
        sent = SentProcessor('Кошка спит.')
        sent.process_text()
        sents.append(sent)
        ex = Exercise(sents)
        ex.find_collocations(1)
        self.assertEqual(ex.lexical_ex, '\nЗадание №6: Выберите одно или несколько слов из списка, которые подходят в предложение по смыслу.\nПоставьте слово в правильную форму.\n_____[девочка, животное, кошка, птица, рыба, собака] спит.\n')
        self.assertEqual(ex.lexical_answers, '\nОтветы на задание №6:\nКошка спит.')

    def test_find_collocations_no_nouns(self):
        sents = []
        sent = SentProcessor('Крепко спит.')
        sent.process_text()
        sents.append(sent)
        ex = Exercise(sents)
        ex.find_collocations(1)
        self.assertEqual(ex.lexical_ex, '\nЗадание №6: Выберите одно или несколько слов из списка, которые подходят в предложение по смыслу.\nПоставьте слово в правильную форму.\nКрепко спит.\n')
        self.assertEqual(ex.lexical_answers, '\nОтветы на задание №6:\nКрепко спит.')

    def test_synonyms(self):
        word = Word('холодный', 0)
        word.extract_synonyms_antonyms('холодный')
        correct = {'ледяной', 'студёный', 'холодный'}
        res = word.get_synonyms()
        test_value = []
        if len(correct) == len(res):
            for el in correct:
                if el in res:
                    test_value.append(True)
        msg = 'Something is wrong'
        self.assertTrue(all(test_value), msg)

    def test_antonyms(self):
        word = Word('холодный', 0)
        word.extract_synonyms_antonyms('холодный')
        correct = {'нехолодный', 'теплый по цвету', 'теплый'}
        res = word.get_antonyms()
        test_value = []
        if len(correct) == len(res):
            for el in correct:
                if el in res:
                    test_value.append(True)
        msg = 'Something is wrong'
        self.assertTrue(all(test_value), msg)

    def test_run_exercises_correct_ex_exist(self):
        sents = []
        sent = SentProcessor('Кошка спит.')
        sent.process_text()
        sents.append(sent)
        ex = Exercise(sents, number_of_sent_in_each_ex=1)
        ex.run_exercises([3, 6])
        value = False
        if (len(ex.compose_ex) != 0) and \
            (len(ex.compose_answers) != 0) and \
            (len(ex.lexical_ex) != 0) and \
            (len(ex.lexical_answers) != 0):
            value = True
        self.assertTrue(value, msg='Упражнения не сформированы')

    def test_run_exercises_wrong_ex_run(self):
        sents = []
        sent = SentProcessor('Кошка спит.')
        sent.process_text()
        sents.append(sent)
        ex = Exercise(sents, number_of_sent_in_each_ex=1)
        ex.run_exercises([3, 6, 4, 5])
        value = False
        if (len(ex.synonym_ex) == 0) and \
                (len(ex.synonym_answers) == 0) and \
                (len(ex.antonym_ex) == 0) and \
                (len(ex.antonym_answers) == 0):
            value = True
        self.assertTrue(value, msg='Лишние упражнения сформированы')

    def test_form_exercises(self):
        sents = []
        sent = SentProcessor('Кошка.')
        sent.process_text()
        sents.append(sent)
        ex = Exercise(sents, number_of_sent_in_each_ex=1)
        ex.run_exercises([3])
        exercises, answers = ex.form_exercises()
        self.assertEqual(exercises, '\nЗадание №3. Составьте предложение из слов '
                                    'и поставьте их в правильную форму:\n[кошка]\n')
        self.assertEqual(answers, '\nОтветы на задание №3:\nКошка.\n')

    def test_form_exercises_before_form(self):
        sents = []
        sent = SentProcessor('Кошка спит.')
        sent.process_text()
        sents.append(sent)
        ex = Exercise(sents, number_of_sent_in_each_ex=1)
        with self.assertRaises(NothingToWriteError):
            ex.form_exercises()
