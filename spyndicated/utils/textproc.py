# D.Temkin : spyndicated.utils.textproc (v0.3.1-1) - Copyright LGPLv3 (2018)

from collections import Counter
from string import ascii_lowercase, digits, punctuation

import numpy as np
import spacy
from gensim.corpora import Dictionary
from gensim.models import LdaModel

from spyndicated import get_config
from spyndicated.plugins import json as json_plugin
from spyndicated.utils.utils import os, find_next_filename

nlp = spacy.load("en")


def stops_list(file="stopwords.lst"):
    stops = open(get_config(filename=file))
    stops_list = [s.lower() for s in stops.readlines()]
    stops_list.extend(list("".join([punctuation, digits, ascii_lowercase])))
    return stops_list


def tags_generator(text_block, ntags=10, **kwargs):
    stops = kwargs.get('stopwords', stops_list())
    base_tokens = tokenizer(text_block, stops=stops)
    tokens = [x.text.lower().capitalize() for x in base_tokens if x.tag_ in ["NNP", "NN"]]
    cnt = Counter(tokens)

    return [x[0] for x in cnt.most_common(n=ntags)]


def tokenizer(text_block, stops):
    doc = nlp(text_block)
    tokens = [x for x in doc if x.text.lower() not in stops]
    return tokens


def doc2bow(doc, **kwargs):
    stops = kwargs.get("stopwords", stops_list())
    tokens = tokenizer(doc, stops=stops)
    return np.array(tokens, dtype=np.str)


class TopicsCorpus(object):

    def __init__(self):
        self.dictionary = None
        self.file = get_config(os.path.join("fitted_models", "lda_corpus.dict"))

    def load(self):
        self.dictionary = Dictionary()
        self.dictionary.load_from_text(fname=self.file)

    def update(self, docs, **kwargs):
        '''

        :param docs:
        :param kwargs:
        :return:
        '''
        dups = kwargs.get('dups', 'skip')
        save = kwargs.get("save", True)
        overwrite = kwargs.get("overwrite", True)
        if self.dictionary is None:
            raise TypeError("Must create Dictionary instance using load or build methods")
        else:
            if dups == 'skip':
                for item_key, item_val in self.dictionary.items():
                    if item_val in docs:
                        docs.remove(item_val)
                    else:
                        pass
                self.dictionary.add_documents(documents=docs)
            elif dups == 'ignore':
                self.dictionary.add_documents(documents=docs)
            else:
                raise ValueError("invalid 'dups' argument value. must be 'skip' or 'ignore'")

            if save is True:
                if overwrite is True:
                    self.dictionary.save_as_text(open(self.file, mode='w'))
                    print("Updated Corpus saved to %s" % self.file)
                elif overwrite is False:
                    d, f = os.path.split(self.file)
                    fx = find_next_filename(d, f)
                    self.dictionary.save_as_text(open(fx, mode='w'))
                    print("Updated Corpus saved to %s" % fx)
                else:
                    raise TypeError("overwrite argument must be boolean")

    def build(self, docs):
        self.dictionary = Dictionary(documents=docs)
        self.dictionary.save_as_text(fname=open(self.file, mode='w'))
        print("Corpus saved to %s" % self.file)


class TopicModel(object):

    def __init__(self, source, corpus):
        self.existing_docs = json_plugin.JSONHandler().select(identifiers=dict(source_name=source))
        self._model = None
        self.source = source
        if isinstance(corpus, TopicModel):
            self.corpus = corpus
        else:
            raise TypeError("Must be a valid TopicCorpus instance")

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, x):
        self._model = x

    def update_corpus(self, docs):
        self.corpus.update_corpus(docs=docs)
        self.model.update(corpus=self.corpus)

    def load(self, file):
        model = LdaModel()
        f = get_config(os.path.join("fitted_models", file))
        if os.path.isfile(f):
            model.load(fname=file)
            self.model = model
        else:
            raise FileNotFoundError("Fitted Model Not Found.")

    def create(self, num_topics, save=True, overwrite=True, *args, **kwargs):
        model = LdaModel(corpus=self.corpus, num_topics=num_topics, *args, **kwargs)
        if save is True:
            if overwrite is True:
                file = get_config(os.path.join("fitted_models", 'lda-%s.pkl' % self.source))
                model.save(fname=open(file, mode='w'))
            else:
                fx = find_next_filename(directory=get_config("fitted_models"), filename="lda-%s.pkl" % self.source)
                model.save(fname=open(get_config(os.path.join("fitted_models", fx)), mode='w'))
        self.model = model

    def prob_dist(self, bow):
        if self.model is None:
            raise NotImplementedError("Must first initialize model using load or create method")
        else:

            return self.model[bow]

    def get_document_topics(self, doc):
        if self.model is None:
            raise NotImplementedError("Must first initialize model using load or create method")

    def get_term_topics(self, term_id, *args, **kwargs):
        if self.model is None:
            raise NotImplementedError("Must first initialize model using load or create method")
        else:
            self.model.get_term_topics(word_id=term_id, *args, **kwargs)

    def get_topic_terms(self, topic_id, top_n=20):
        if self.model is None:
            raise NotImplementedError("Must first initialize model using load or create method")
        else:
            self.model.get_topic_terms(topicid=topic_id, topn=top_n)

    def get_topics(self):
        if self.model is None:
            raise NotImplementedError("Must first initialize model using load or create method")
        else:
            return self.model.get_topics()

    def infer(self, docpart, sstats=False):
        if self.model is None:
            raise NotImplementedError("Must first initialize model using load or create method")
        else:
            self.model.inference(chunk=docpart, collect_sstats=sstats)

    def reform(self, chunk, mod_state=None):
        if self.model is None:
            raise NotImplementedError("Must first initialize model using load or create method")
        else:
            e = self.model.do_estep(chunk=chunk, state=mod_state)
            print(e)
