# D.Temkin : [pkgpath] (v[pkgver]-[modver]) - Copyright LGPLv3 (2018)

import json
import os
import re
from abc import abstractmethod
from collections import Counter
from string import punctuation, digits, ascii_lowercase

import numpy as np
from nltk.stem.snowball import SnowballStemmer


class Data(object):

    def __init__(self, lst=None):
        file = os.path.join(os.getcwd(), 'spyndicated', '.data', 'master.json')
        if lst is None:
            self.initlist = self.read_data(datafile=file)
        else:
            self.initlist = lst

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

    def keyword_cleaner(self, kwds):
        puncts = list(punctuation)
        stemmer = SnowballStemmer("english")
        clean = []
        for k in range(len(kwds)):
            if (kwds[k].isdigit() and len(kwds[k]) != 4):
                print("Removing digit that is not length 4 (i.e. years)")
                print(kwds[k])
                pass

            elif kwds[k].find("\n") > -1:
                print("Removing keyword containing newline character")
                print(kwds[k])
                pass

            elif len(kwds[k]) < 3:
                print("Removing keyword that is less than 3 characters")
                print(kwds[k])
                pass

            elif kwds[k].find("http") > -1:
                print("Removing keyword containing 'http'")
                print(kwds[k])
                pass

            elif kwds[k].find("(") > -1:
                print("Removing keyword containing '('")
                print(kwds[k])
                pass

            elif kwds[k] in self._stops:
                print("Removing keyword found in stopwords list")
                print(kwds[k])
                pass

            elif any((p for p in puncts if kwds[k].find(p) > -1)):
                print("Removing key containing any punctuation mark.")
                print(kwds[k])
                pass
            else:
                clean.append(kwds[k])

        print("\nnumber of kwds (after cleaning): %s\n" % str(len(clean)))
        print("Keywords (after cleaning): \n")
        print(clean)
        print("\nApplying Stemmer\n")
        return [stemmer.stem(x) for x in clean]


    def keyword_parser(self, lst, **kwargs):
        stops = kwargs.get('stops', self._stops)
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


class AbstractSet(object):

    def __init__(self, data, max_size):
        assert (isinstance(data, Data) is True), "Oops"
        self.data = data
        if type(max_size) is float:
            self.size = int(len(self.data.ids) * max_size)
        elif type(max_size) is int:
            if max_size > .8 * len(self.data.ids):
                print("WARNING, using over 80% of the original data set as training data.")

            self.size = int(len(self.data.ids) * max_size)

    @property
    @abstractmethod
    def ids(self):
        raise NotImplementedError()

    @property
    def keywords_as_docs(self):
        return self.data.keyword_parser(lst=self.entries)[1]

    @property
    def keywords(self):
        return self.data.keyword_parser(lst=self.entries)[0]

    @property
    def entries(self):
        return [self.data.entries[i] for i in self.ids]


class TrainingSet(AbstractSet):

    def __init__(self, data, max_size):
        super().__init__(data=data, max_size=max_size)

    @property
    def ids(self):
        return set(np.random.choice(a=list(self.data.ids), size=self.size, replace=False))


class TestingSet(AbstractSet):

    def __init__(self, data, max_size, exclude_ids=None):
        super().__init__(data=data, max_size=max_size)
        if exclude_ids is None:
            self.available_ids = self.data.ids
        else:
            self.available_ids = self.data.ids - exclude_ids

    @property
    def ids(self):
        if self.size == 'all':
            return self.available_ids
        else:
            return set(np.random.choice(a=list(self.available_ids), size=self.size, replace=False))


class ValidationSet(AbstractSet):

    def __init__(self, data, max_size, exclude_ids=None):
        super().__init__(data=data, max_size=max_size)

        if exclude_ids is None:
            self.available_ids = self.data.ids
        else:
            self.available_ids = self.data.ids - exclude_ids

    @property
    def ids(self):
        if self.size == 'all':
            return self.available_ids
        else:
            return set(np.random.choice(a=list(self.available_ids), size=self.size, replace=False))
