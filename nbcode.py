# D.Temkin : [pkgpath] (v[pkgver]-[modver]) - Copyright LGPLv3 (2018)

import json
import os
import re
import sys
import warnings
from collections import Counter
from string import punctuation, digits, ascii_lowercase

import numpy as np
from nltk.stem.snowball import SnowballStemmer

if not sys.warnoptions:
    warnings.simplefilter("ignore")

from plotly.offline import init_notebook_mode, plot, iplot
from plotly import graph_objs as go
import pyLDAvis.gensim as ldaviz

plotting_pkgs = [init_notebook_mode, plot, iplot, go, ldaviz]


class Data(object):

    def __init__(self, file=os.path.join(os.getcwd(), 'spyndicated',
                                         '.data', 'master.json')):

        self.initlist = self.read_data(datafile=file)
        self._stops = self.read_stopwords()
        self._allkeywords, self._dockwds = self.keyword_parser(lst=self.initlist)

    @property
    def ids(self):
        return set(range(len(self.initlist)))

    @property
    def keywords_as_docs(self):
        return self._dockwds

    @property
    def all_keywords(self):
        return self._allkeywords

    @property
    def keyword_counts(self):
        cnt = dict(Counter(self._allkeywords))
        cnts = {}
        for c in cnt.keys():
            print(cnt[c])
            if cnt[c] > 800:
                pass
            else:
                cnts.update({c: cnt[c]})
        return cnts

    @property
    def stopwords(self):
        return self._stops

    @property
    def entries(self):
        return self.initlist

    @property
    def blog_entries(self):
        return [e for e in self.entries if e['is_blog'] == 1]

    @property
    def news_entries(self):
        return [e for e in self.entries if e['is_blog'] == 0]

    def read_stopwords(self):
        file = open(os.path.join(os.getcwd(), 'spyndicated', '.config', 'stopwords.lst'))
        stops_list = [s.lower().rstrip("\n") for s in file.readlines()]
        stops_list.extend(list("".join([punctuation, digits, ascii_lowercase])))
        return stops_list

    def read_data(self, datafile):
        with open(datafile, mode='r') as f:
            lines = [json.loads(l) for l in f.readlines()]
            return lines

    def keyword_parser(self, lst, **kwargs):
        stops = kwargs.get('stops', self.read_stopwords())
        _allkwds = []
        _dockwds = []
        puncts = list(punctuation)
        stemmer = SnowballStemmer("english")
        for item in lst:
            kwds = []
            for k in range(len(item['kwds'])):
                if (item['kwds'][k].isdigit() and len(item['kwds'][k]) != 4) or \
                        re.match(" +", item['kwds'][k]) is not None or \
                        item['kwds'][k].find("\n") > -1 or \
                        item['kwds'][k] in stops or \
                        len(item['kwds'][k]) < 3 or \
                        item['kwds'][k].find("http") > -1 or \
                        item['kwds'][k].find("(") > -1 or \
                        any((p for p in puncts if item['kwds'][k].find(p) > -1)):
                    pass
                else:
                    kwds.append(stemmer.stem(item['kwds'][k]))
            _allkwds.extend(kwds)
            _dockwds.append(kwds)
        return _allkwds, _dockwds


class TrainingSet(object):

    def __init__(self, data, max_size, w_replacement=False):
        self.data = data
        self.size = max_size
        self.replace = w_replacement

    @property
    def ids(self):
        return set(np.random.choice(a=list(self.data.ids), size=self.size, replace=self.replace))

    @property
    def keywords(self):
        return self.data.keyword_parser(lst=self.__iter__())

    def __iter__(self):
        return [self.data.entries[i] for i in self.ids]

    def __len__(self):
        return len(self.__iter__())


class TestingSet(object):

    def __init__(self, data, max_size, exclude_ids=None, w_replacement=False):
        self.data = data
        self.size = max_size
        self.replace = w_replacement

        if exclude_ids is None:
            self.available_ids = self.data.ids
        else:
            self.available_ids = self.data.ids - exclude_ids

    @property
    def ids(self):
        if self.size == 'all':
            return self.available_ids
        else:
            return set(np.random.choice(a=list(self.available_ids), size=self.size,
                                        replace=self.replace))

    @property
    def keywords(self):
        return self.data.keyword_parser(lst=self.__iter__())

    def __iter__(self):
        return [self.data.entries[j] for j in self.ids]

    def __len__(self):
        return len(self.__iter__())
