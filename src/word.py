from ruwordnet import RuWordNet
from wiki_ru_wordnet import WikiWordnet
from src.constants import PROJECT_ROOT


class Word:

    def __init__(self, token: str, word_id: int):
        self._raw = token
        self.id = word_id
        self.synonyms = set()
        self.antonyms = set()
        self.wikiwordnet = WikiWordnet()
        self.wn = RuWordNet(filename_or_session=str(PROJECT_ROOT/'src'/'ruwordnet-2021.db'))

    def create_antonyms(self, word: str, antonyms: set):
        try:
            for el in self.wn[word]:
                if el.synset.antonyms:
                    if ',' in el.synset.antonyms[0].title:
                        for antonym in el.synset.antonyms[0].title.split(', '):
                            antonyms.add(antonym.lower())
                    else:
                        antonyms.add(el.synset.antonyms[0].title.lower())
        except KeyError:
            return None

    def extract_synonyms_antonyms(self, word: str):
        if self.wikiwordnet.get_synsets(word):
            for w in self.wikiwordnet.get_synsets(word)[0].get_words():
                self.synonyms.add(w.lemma())
                if word != w.lemma():
                    self.create_antonyms(word=w.lemma(), antonyms=self.antonyms)
                self.create_antonyms(word=word, antonyms=self.antonyms)

    def fill_sets(self):
        self.extract_synonyms_antonyms(self._raw)

    def get_synonyms(self):
        return self.synonyms

    def get_antonyms(self):
        return self.antonyms
