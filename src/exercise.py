import os.path
import random
import re
from pathlib import Path
from typing import List

from numpy import dot
import heapq
from pymorphy2 import MorphAnalyzer
from navec import Navec

from src.constants import punctuation, ASSETS_PATH, most_frequent_nouns, most_frequent_adjectives, most_frequent_verbs,\
    most_frequent_adverbs, PROJECT_ROOT
from src.word import Word
from src.files import NothingToWriteError


class SentProcessor:
    """
    Предобрабатывает исходный текст:
    разбивает на токены, находит начальные формы, морфологические признаки и векторы.
    """
    def __init__(self, text: str) -> None:
        if isinstance(text, str):
            self._raw_text = text
        else:
            self._raw_text = None
        self._lemma_text = None
        self._tokens = None
        self._morph_analyzer = MorphAnalyzer()
        self._morph = None
        self._vector = {}

    def _tokenise_text(self) -> None:
        """
        Очищает текст от знаков препинания, приводит к нижнему регистру, разбивает на токены.
        """
        raw_text = self._raw_text
        for el in punctuation:
            raw_text = raw_text.replace(el, ' ')
        self._tokens = raw_text.lower().split()

    def _lemmatise_text(self) -> None:
        """
        Определяет начальные формы токенов.
        """
        self._lemma_text = [self._morph_analyzer.parse(token)[0].normal_form for token in self._tokens]

    def _morph_text(self) -> None:
        """
        Осуществляет морфологический анализ исходного текста:
        Производит разбор текста на морфологические признаки и сохраняет их для каждого токена.
        """
        self._morph = [self._morph_analyzer.parse(token)[0].tag for token in self._tokens]

    def _vectorize_text(self) -> None:
        """
        Предобученная на основе корпуса художественных текстов на русском языке модель
        находит векторы для каждого токена. Пары токен-вектор хранятся в словаре.
        """
        path = PROJECT_ROOT / 'src'/ 'navec_hudlit_v1_12B_500K_300d_100q.tar'
        navec = Navec.load(path)
        for lemma in self._lemma_text:
            if lemma in navec.vocab:
                self._vector[lemma] = navec[lemma]
            else:
                self._vector[lemma] = navec['<pad>']

    def process_text(self) -> None:
        """
        Выполняет предобработку текста.
        """
        self._tokenise_text()
        self._lemmatise_text()
        self._morph_text()
        self._vectorize_text()

    def get_raw_text(self) -> str:
        """
        Возвращает исходный текст.
        """
        return self._raw_text

    def get_tokens(self) -> list:
        """
        Взвращает токены.
        """
        return self._tokens

    def get_lemmas(self) -> list:
        """
        Возвращает словарные формы слов.
        """
        return self._lemma_text

    def get_morph(self) -> list:
        """
        Возвращает морфологические признаки слов.
        """
        return self._morph


    def get_vectors(self) -> dict:
        """
        Возвращает словарь, ключи в котором - токены, а значения - векторы.
        """
        return self._vector

class Exercise:
    def __init__(self, processed_text: List[SentProcessor],
                 number_of_sent_in_each_ex = 5) -> None:
        """
        Инициализирует объект класса Exercise.
        """
        self._morph_analyzer = MorphAnalyzer()
        self.processed_text = processed_text
        self.number_of_sent_in_each_ex = number_of_sent_in_each_ex
        self.synonym_ex = ''
        self.synonym_answers = ''
        self.antonym_ex = ''
        self.antonym_answers = ''
        self.compose_ex = ''
        self.compose_answers = ''
        self.case_ex = ''
        self.case_answers = ''
        self.forms_ex = ''
        self.forms_answers = ''
        self.lexical_ex = ''
        self.lexical_answers = ''

    def run_exercises(self, ex_list=None) -> None:
        """
        Запускает скрипт создания всех упражнений.
        """
        if ex_list is None:
            ex_list = [1, 2, 3, 4, 5, 6]
        if 1 in ex_list:
            self.generate_synonyms()
        if 2 in ex_list:
            self.generate_antonyms()
        if 3 in ex_list:
            self.generate_scrambled_sentence()
        if 4 in ex_list:
            self.generate_case_exercise()
        if 5 in ex_list:
            self.select_grammatical_form(self.number_of_sent_in_each_ex)
        if 6 in ex_list:
            self.find_collocations(self.number_of_sent_in_each_ex)

    def form_exercises(self) -> tuple[str, str]:
        '''
        Объединяет все упражнения в один файл.
        '''
        all_exercises = (self.synonym_ex +
                         self.antonym_ex +
                         self.compose_ex +
                         self.case_ex +
                         self.forms_ex +
                         self.lexical_ex)
        all_answers = (self.synonym_answers +
                       self.antonym_answers +
                       self.compose_answers +
                       self.case_answers +
                       self.forms_answers +
                       self.lexical_answers)
        if len(all_exercises) == 0 or len(all_answers) == 0:
            raise NothingToWriteError
        return all_exercises, all_answers

    def generate_synonyms(self) -> None:
        """
        Генерирует упражнение на синонимы.
        """
        sentence = random.choice(self.processed_text)
        lemmas = sentence.get_lemmas()
        synonyms = {}
        while len(synonyms) < 1:
            lemma = random.choice(lemmas)
            idx = lemmas.index(lemma)
            word = Word(lemma, idx)
            word.fill_sets()
            if len(word.get_synonyms()) >= 2:
                synonyms[idx] = word.get_synonyms()

        new_sentence = sentence.get_tokens()
        if len(synonyms) == 0:
            self.synonym_ex = 'Нет заданий с синонимами'
            return
        target_word, correct, synonym_task, = self._get_options(synonyms, lemmas)
        new_sentence[target_word] = new_sentence[target_word].upper()
        self.synonym_ex = f"""Выберите синоним к выделенному слову: \n
{' '.join(new_sentence)} \n
{synonym_task}\n"""
        self.synonym_answers = f'Правильный ответ:{correct}\n'

    def generate_antonyms(self) -> None:
        """
        Генерирует упражнение на антонимы.
        """
        sentence = random.choice(self.processed_text)
        lemmas = sentence.get_lemmas()
        antonyms = {}
        while len(antonyms) < 1:
            lemma = random.choice(lemmas)
            idx = lemmas.index(lemma)
            word = Word(lemma, idx)
            word.fill_sets()
            if word.get_antonyms():
                antonyms[idx] = word.get_antonyms()

        new_sentence = sentence.get_tokens()
        if len(antonyms) == 0:
            self.antonym_ex = 'Нет заданий с антонимами'
            return
        target_word, correct, antonym_task = self._get_options(antonyms, lemmas)
        new_sentence[target_word] = new_sentence[target_word].upper()
        self.antonym_ex = f"""Выберите антоним к выделенному слову: \n
{' '.join(new_sentence)} \n
{antonym_task}\n"""
        self.antonym_answers = f'Правильный ответ:{correct}\n'

    def _get_options(self, thesaurus: dict, lemmas: list[str]) -> tuple[int, int, str]:
        """
        Cоздает список вариантов, номер правильного ответа.
        """
        answer = ''
        word_id = 0
        num_words = 0
        while num_words < 1:
            word_id = list(thesaurus.keys())[0]
            answer = random.sample(list(thesaurus[word_id]), 1)[0]
            if answer == lemmas[word_id]:
                num_words = 0
            else:
                num_words = len(thesaurus[word_id])
        pos = self._morph_analyzer.parse(lemmas[word_id])[0].tag
        options = ['нет', 'правильного', 'ответа']
        if 'NOUN' in pos:
            options = most_frequent_nouns
        if 'ADJF' in pos:
            options = most_frequent_adjectives
        if 'INFN' in pos:
            options = most_frequent_verbs
        if 'ADVB' in pos:
            options = most_frequent_adverbs
        task_choices = set(random.sample(options, 3))
        if answer not in task_choices:
            task_choices.add(answer)
        else:
            task_choices.add(random.choice(options))
        final_choices = list(task_choices)
        correct = final_choices.index(answer) + 1
        task = f"""Варианты:\n 
1 - {final_choices[0].upper()} \n 
2 - {final_choices[1].upper()} \n 
3 - {final_choices[2].upper()} \n 
4 - {final_choices[3].upper()}"""
        return word_id, correct, task

    def generate_scrambled_sentence(self) -> None:
        """
        Генерирует упражнение на составление предложения из лемм.
        """
        sentence = random.choice(self.processed_text)
        lemmas = sentence.get_lemmas()
        random.shuffle(lemmas)

        lemmatized_tokens = ', '.join(f'[{lemma}]' for lemma in lemmas)

        exercise_task = f"\nЗадание №3. Составьте предложение из слов и поставьте их в правильную форму:\n{lemmatized_tokens}\n"

        full_text = f'\nОтветы на задание №3:\n{sentence.get_raw_text()}\n'

        self.compose_ex = exercise_task
        self.compose_answers = full_text

    def generate_case_exercise(self) -> None:
        """
        Генерирует упражнение на определение падежа существительного в предложении.
        """
        random_sentence = random.choice(self.processed_text)
        sentence_tokens = list(random_sentence.get_tokens())

        noun_candidates = [word for word in sentence_tokens if 'NOUN' in self._morph_analyzer.parse(word)[0].tag]

        if not noun_candidates:
            self.fourth_ex = "В данном предложении нет существительных."

        random.shuffle(sentence_tokens)

        selected_noun = random.choice(noun_candidates)
        selected_noun_upper = selected_noun.upper()

        raw_random_sentence = random_sentence.get_raw_text()

        cases_dict = {
            'nomn': 'Именительный',
            'gent': 'Родительный',
            'datv': 'Дательный',
            'accs': 'Винительный',
            'ablt': 'Творительный',
            'loct': 'Предложный'
        }

        correct_case_abbr = self._morph_analyzer.parse(selected_noun)[0].tag.case
        correct_case = cases_dict.get(correct_case_abbr)

        exercise_task = f"\nЗадание №4: Выберите правильный падеж для слова '{selected_noun_upper}' в предложении '{raw_random_sentence}':\n"

        for case_num, case_abbr in enumerate(cases_dict, start=1):
            exercise_task += f"{case_num}. {cases_dict[case_abbr]}\n"

        full_text = f"\nОтветы на задание №4:\nПравильный ответ: {correct_case}\n"

        self.case_ex = exercise_task
        self.case_answers = full_text

    def select_grammatical_form(self, number_of_sent) -> None:
        """
        Генерирует упражнение на выбор правильной формы слова.
        """
        sentences = random.sample(self.processed_text, number_of_sent)
        full_text = '\nОтветы на задание №5: \n'
        text = '\nЗадание №5: Поставьте слово в скобках в правильную форму:\n'

        for sent in sentences:
            sent_text = sent.get_raw_text()
            full_text += sent_text + '\n'
            morphs = sent.get_morph()
            tokens = sent.get_tokens()
            lemmas = sent.get_lemmas()
            possible_change = []

            for i in range(len(tokens)):
                if ('NOUN' in str(morphs[i])) or ('VERB' in str(morphs[i])):
                    possible_change.append(i)

            if len(possible_change) >= 3:
                number_gaps = 3
            else:
                number_gaps = len(possible_change)

            to_change_index = random.sample(possible_change, number_gaps)
            to_change = {}

            for ind in to_change_index:
                to_change[tokens[ind]] = f'_____ [{lemmas[ind]}]'

            for old, new in to_change.items():
                pattern = re.compile(old, re.IGNORECASE)
                sent_text = pattern.sub(new, sent_text)

            text += sent_text + '\n'

        self.forms_ex = text
        self.forms_answers = full_text

    def find_collocations(self, number_sent) -> None:
        """
        Генерирует упражнение на поиск коллокаций для предложенных слов.
        """
        sentences = random.sample(self.processed_text, number_sent)
        full_text = '\nОтветы на задание №6:'
        text = '\nЗадание №6: Выберите одно или несколько слов из списка, которые подходят в предложение по смыслу.\nПоставьте слово в правильную форму.\n'
        path =  PROJECT_ROOT / 'src'/ 'navec_hudlit_v1_12B_500K_300d_100q.tar'
        navec = Navec.load(path)

        for sent in sentences:
            sent_text = sent.get_raw_text()
            full_text += '\n' + sent_text
            vectors = sent.get_vectors()
            tokens = sent.get_tokens()
            lemmas = sent.get_lemmas()
            morphs = sent.get_morph()
            possible_change = {}

            for i in range(len(tokens)):
                if 'NOUN' in str(morphs[i]):
                    possible_change[tokens[i]] = lemmas[i]

            if len(possible_change) > 0:
                change_token = random.sample(possible_change.keys(), 1)[0]
                change_lemma = possible_change[change_token]
                change_vector = vectors[change_lemma]

                other_nouns = {}

                for noun in most_frequent_nouns:
                    other_vector = navec[noun]
                    cosine = dot(change_vector, other_vector)
                    other_nouns[cosine] = noun
                other_keys = heapq.nlargest(5, other_nouns.keys())

                new = []
                for key in other_keys:
                    most_similar_noun = other_nouns[key]
                    new.append(most_similar_noun)
                if change_lemma not in new:
                    new.append(change_lemma)
                new = sorted(new)
                answers = ', '.join(new)

                pattern = re.compile(change_token, re.IGNORECASE)
                sent_text = pattern.sub(f'_____[{answers}]', sent_text)

            text += sent_text + '\n'

        self.lexical_ex = text
        self.lexical_answers = full_text

