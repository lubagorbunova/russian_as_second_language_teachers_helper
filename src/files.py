import shutil

from pathlib import Path
from src.constants import ASSETS_PATH
from typing import Union


class EmptyFileError(BaseException):
    """
    Файл пустой.
    """


class NoFileError(BaseException):
    """
    Файл не указан.
    """


class NothingToWriteError(BaseException):
    """
    В файл ничего не записывается.
    """


class Files:
    def __init__(self, file_name: str):
        self.file_name = file_name
        self.text_path = ASSETS_PATH.parent / file_name

    def read_file(self) -> str:
        """
        Читает файл. Жалуется, если файл пустой.
        """
        with open(self.text_path, encoding='utf-8') as file:
            text = file.read()
        if len(text)==0:
            raise EmptyFileError
        return text

    def get_exercises_path(self) -> Path:
        """
        Возвращает путь к файлу, в котором будут храниться упражнения.
        """
        if self.file_name == '':
            raise NoFileError
        exercise_name = f"{self.file_name[:self.file_name.index('.')]}_exercises.txt"
        return ASSETS_PATH / exercise_name

    def get_answers_path(self) -> Path:
        """
        Возвращает путь к файлу, в котором будут храниться ответы на упражнения.
        """
        if self.file_name == '':
            raise NoFileError
        answer_name = f"{self.file_name[:self.file_name.index('.')]}_answers.txt"
        return ASSETS_PATH / answer_name

    def write_to_file(self, ex_text: str, answer_text: str, answers_path = None,
                      exercises_path = None) -> None:
        """
        Записывает упражнения и ответы в файлы, которые передаются пользователю.
        """
        if answers_path == None:
            answers_path = self.get_answers_path()
        if exercises_path == None:
            exercises_path = self.get_exercises_path()
        if (len(ex_text) == 0) or (len(answer_text) == 0):
            raise NothingToWriteError
        with open(exercises_path, 'w', encoding='utf-8') as file_1:
            file_1.write(ex_text)
        with open(answers_path, 'w', encoding='utf-8') as file_2:
            file_2.write(answer_text)
