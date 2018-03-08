# D.Temkin : [pkgpath] (v[pkgver]-[modver]) - Copyright LGPLv3 (2018)

import json
import os
import re
from abc import ABCMeta, abstractmethod
from collections import Counter
from string import punctuation, digits, ascii_lowercase

import numpy as np
from nltk.stem.snowball import SnowballStemmer


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


class AbstractSet(metaclass=ABCMeta):

    def __init__(self, data, max_size, w_replacement=False):
        self.data = data
        self.size = max_size
        self.replace = w_replacement

    @abstractmethod
    @property
    def ids(self):
        raise NotImplementedError()

    @property
    def keywords(self):
        return self.data.keyword_parser(lst=self.__iter__())

    @property
    def blog_keywords(self):
        return self.data.keyword_parser(lst=[i for i in self.__iter__() if i['is_blog'] == 1])

    @property
    def news_keywords(self):
        return self.data.keyword_parser(lst=[i for i in self.__iter__() if i['is_blog'] == 0])

    def __iter__(self):
        return [self.data.entries[i] for i in self.ids]

    def __len__(self):
        return len(self.__iter__())


class TrainingSet(AbstractSet):

    def __init__(self, data, max_size, w_replacement=False):
        super().__init__(data=data, max_size=max_size, w_replacement=w_replacement)

    @property
    def ids(self):
        return set(np.random.choice(a=list(self.data.ids), size=self.size, replace=self.replace))


class TestingSet(AbstractSet):

    def __init__(self, data, max_size, exclude_ids=None, w_replacement=False):
        super().__init__(data=data, max_size=max_size, w_replacement=w_replacement)
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

#
# blogkwds = []
# blogtags = []
# blogtopics = []
# newskwds = []
# newstags = []
# newstopics = []
#
# for j in range(len(testing_entries)):
#     ent = testing_entries[j]
#     for tag in ent['tags']:
#         tt = []
#         if type(tag) is list:
#             tt.append(tag[0])
#         else:
#             tt.append(tag)
#         if len(tt) > 0:
#             ent.update({"tags": tt})
#         else:
#             pass
#
#     if ent['is_blog'] == 1:
#         blogkwds.extend([i for i in ent['kwds']])
#         blogtags.extend([i.split(",")[0] for i in ent['tags']])
#         blogtopics.extend([i[0] for i in ent['topics']])
#     else:
#         newskwds.extend([i for i in ent['kwds']])
#         newstags.extend([i for i in ent['tags']])
#         newstopics.extend([i[0] for i in ent['topics']])


# kwd_layout = go.Layout(barmode='overlay', title='Keyword Probabilities by Source Type')
# BlogKeywords = go.Histogram(x=blogkwds, name='Blog Keywords', histnorm='probability', opacity=0.75)
# NewsKeywords = go.Histogram(x=newskwds, name='News Keywords', histnorm='probability', opacity=0.75)
# kwd_traces = [BlogKeywords, NewsKeywords]
# kwd_fig = go.Figure(data=kwd_traces, layout=kwd_layout)
# iplot(kwd_fig)
#
# tag_layout = go.Layout(barmode='overlay', title='Tag Frequencies by Source Type')
# BlogTags = go.Histogram(x=blogtags, name='Blog Tags', opacity=0.75)
# NewsTags = go.Histogram(x=newstags, name='News Tags', opacity=0.75)
# tag_traces = [BlogTags, NewsTags]
# tag_fig = go.Figure(data=tag_traces, layout=tag_layout)
# iplot(tag_fig)
#
# topics_layout = go.Layout(barmode='overlay', title='Topic Probabilities by Source Type')
# BlogTopics = go.Histogram(x=blogtopics, name='Blog Topics', histnorm='probability', opacity=0.75)
# NewsTopics = go.Histogram(x=newstopics, name='News Topics', histnorm='probability', opacity=0.75)
# topics_traces = [BlogTopics, NewsTopics]
# topics_fig = go.Figure(data=topics_traces, layout=topics_layout)
# iplot(topics_fig)
