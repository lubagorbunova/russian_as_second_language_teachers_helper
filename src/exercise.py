import random
import re
from typing import List

from numpy import dot
import heapq
from pymorphy2 import MorphAnalyzer
from navec import Navec

from src.constants import most_frequent_nouns, PROJECT_ROOT
from src.files import NothingToWriteError
from src.sentence_processor import SentProcessor


class Exercise:
    def __init__(self, processed_text: List[SentProcessor],
                 number_of_sent_in_each_ex=5) -> None:
        """
        Инициализирует объект класса Exercise.
        """
        self._morph_analyzer = MorphAnalyzer()
        self.processed_text = processed_text
        self.number_of_sent_in_each_ex = number_of_sent_in_each_ex
        self.tasks = {1: 'Составьте предложение из слов и поставьте их в правильную форму',
                      2: 'Выберите правильный падеж для слова',
                      3: 'Поставьте слово в скобках в правильную форму',
                      4: 'Выберите одно или несколько слов из списка, которые подходят в предложение по смыслу.\nПоставьте слово в правильную форму'}

    def beautiful_task(func):
        def wrapper(self, *arg, **kw):
            ex, answ, ex_n, task = func(self, *arg, **kw)
            modified_result = f'\nЗадание №{ex_n}. {task}:\n{ex}\n\nОтветы на задание {ex_n}:\n{answ}\n'
            return modified_result
        return wrapper

    def run_exercises(self, ex_list=None) -> str:
        """
        Запускает скрипт создания всех упражнений.
        """
        if 1 in ex_list:
            res = self.generate_scrambled_sentence()
        if 2 in ex_list:
            res = self.generate_case_exercise()
        if 3 in ex_list:
            res = self.select_grammatical_form(self.number_of_sent_in_each_ex)
        if 4 in ex_list:
            res = self.find_collocations(self.number_of_sent_in_each_ex)
        return res

    @beautiful_task
    def generate_scrambled_sentence(self) -> None:
        """
        Генерирует упражнение на составление предложения из лемм.
        """
        ex_number = 1

        sentence = random.choice(self.processed_text)
        lemmas = sentence.get_lemmas()
        random.shuffle(lemmas)

        lemmatized_tokens = ', '.join(f'[{lemma}]' for lemma in lemmas)
        
        return lemmatized_tokens, sentence.get_raw_text(), ex_number, self.tasks[ex_number]

    @beautiful_task
    def generate_case_exercise(self) -> None:
        """
        Генерирует упражнение на определение падежа существительного в предложении.
        """
        ex_number = 2
        random_sentence = random.choice(self.processed_text)
        sentence_tokens = list(random_sentence.get_tokens())

        noun_candidates = [word for word in sentence_tokens if 'NOUN' in self._morph_analyzer.parse(word)[0].tag]

        if not noun_candidates:
            self.case_ex = "В данном предложении нет существительных."

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

        exercise_task = f"'{selected_noun_upper}' в предложении '{raw_random_sentence}':\n"

        for case_num, case_abbr in enumerate(cases_dict, start=1):
            exercise_task += f"{case_num}. {cases_dict[case_abbr]}\n"

        return exercise_task, correct_case, ex_number, self.tasks[ex_number]

    @beautiful_task
    def select_grammatical_form(self, number_of_sent) -> None:
        """
        Генерирует упражнение на выбор правильной формы слова.
        """
        ex_number = 3
        if len(self.processed_text) < 5:
            number_of_sent = len(self.processed_text)

        sentences = random.sample(self.processed_text, number_of_sent)
        full_text = ''
        text = ''

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

        return text, full_text, ex_number, self.tasks[ex_number]

    @beautiful_task
    def find_collocations(self, number_sent) -> None:
        """
        Генерирует упражнение на поиск коллокаций для предложенных слов.
        """
        ex_number = 4
        if len(self.processed_text) < 5:
            number_sent = len(self.processed_text)

        sentences = random.sample(self.processed_text, number_sent)
        full_text = ''
        text = ''
        path = PROJECT_ROOT / 'src' / 'navec_hudlit_v1_12B_500K_300d_100q.tar'
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
        return text, full_text, ex_number, self.tasks[ex_number]
