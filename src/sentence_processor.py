from pymorphy2 import MorphAnalyzer
from navec import Navec

from src.constants import punctuation, PROJECT_ROOT


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
        path = PROJECT_ROOT / 'src' / 'navec_hudlit_v1_12B_500K_300d_100q.tar'
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
