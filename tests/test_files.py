import unittest
from src.files import Files, EmptyFileError, NoFileError, NothingToWriteError
from src.constants import ASSETS_PATH_TESTS, ASSETS_PATH


class FilesBaseTests(unittest.TestCase):
    def test_readfile_content(self):
        instance = Files('fortest.txt')
        instance.text_path = ASSETS_PATH_TESTS.parent / instance.file_name
        self.assertEqual(instance.read_file(), 'Кошка спит на диване.')

    def test_readfile_notempty(self):
        instance = Files('fortestempty.txt')
        instance.text_path = ASSETS_PATH_TESTS.parent / instance.file_name
        with self.assertRaises(EmptyFileError):
            instance.read_file()

    def test_getexercisepass(self):
        instance = Files('fortest.txt')
        exercise_name = f"{instance.file_name[:instance.file_name.index('.')]}_exercises.txt"
        self.assertEqual(instance.get_exercises_path(), ASSETS_PATH /exercise_name)

    def test_getexercisepass_nofilename(self):
        instance = Files('')
        with self.assertRaises(NoFileError):
            instance.get_exercises_path()

    def test_get_answerspass(self):
        instance = Files('fortest.txt')
        answers_name = f"{instance.file_name[:instance.file_name.index('.')]}_answers.txt"
        self.assertEqual(instance.get_answers_path(), ASSETS_PATH / answers_name)

    def test_get_answerspass_incorrect(self):
        instance = Files('')
        with self.assertRaises(NoFileError):
            instance.get_answers_path()

    def test_writetofile_content(self):
        instance = Files('fortest.txt')
        instance.text_path = ASSETS_PATH.parent / instance.file_name
        instance.write_to_file('вопросы', 'ответы', answers_path=ASSETS_PATH_TESTS / 'fortest_answers.txt',
                               exercises_path=ASSETS_PATH_TESTS / 'fortest_answers.txt')
        with open(ASSETS_PATH_TESTS / 'fortest_exercises.txt', encoding='utf-8') as file:
            ex = file.read()
        self.assertEqual('вопросы', ex)
        with open(ASSETS_PATH_TESTS / 'fortest_answers.txt', encoding='utf-8') as file:
            answers = file.read()
        self.assertEqual('ответы', answers)

    def test_writetofile_incorrect(self):
        instance = Files('fortest.txt')
        with self.assertRaises(NothingToWriteError):
            instance.write_to_file('', '')
