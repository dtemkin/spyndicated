# D.Temkin : spyndicated.rss.base (v0.3.1-1) - Copyright LGPLv3 (2018)

import html
import re
from collections import UserDict
from datetime import datetime, timedelta
from queue import Queue
from string import Template

import feedparser
from bs4 import BeautifulSoup as bsoup

from spyndicated.usr import Profile
from spyndicated.utils.textproc import tags_generator


class Entry(UserDict):

    def __init__(self, source_name):
        super().__init__()
        self.update({
            "source_name": source_name,
            "curr_rank": 1.0, "prev_rank": 1.0
        })

    def _tags_parser(self, d):
        if "tags" in d.keys():
            return [tag["term"] for tag in d["tags"]]
        else:
            try:
                s = self["summary"]
            except KeyError:
                raise KeyError("Must generate cleaned summary before parsing tags")
            else:
                if s is None:
                    return None
                else:
                    return tags_generator(text_block=s)

    def _clean_text(self, text):

        htmlpatt = re.compile('<.*?>')
        text = re.sub(htmlpatt, " ", html.unescape(text))
        text = re.sub('\.\.\..*?', "", text)
        text = re.sub('.?Read More\W', "", text)
        return text

    def _build_template_string(self):
        t = Template("$source:  $title\n========\n$pub_datetime - $author - $tags"
                     "\n\n-----------------------------\n")
        t.safe_substitute(self)
        return t

    @staticmethod
    def _locate_image(d):

        inline_img_patt = re.compile('(<img src).*?/>')
        match = re.search(inline_img_patt, d["summary"])
        if match:
            s = bsoup(match.string).find("img").attrs["src"]
            if s.find("http:") < 0:
                s = "http:" + s
            return s
        elif 'media_content' in d.keys():
            try:
                imgloc = d['media_content'][0]['url']
            except:
                return None
            else:
                return imgloc
        else:
            return None

    @staticmethod
    def _alt_pubdate(adjust, adjust_per, fmt="%Y-%m-%d %H:%M:%S"):
        dt = datetime.now()
        if adjust_per.lower() == "s":
            dt = dt - timedelta(seconds=adjust)
        elif adjust_per.lower() == "m":
            dt = dt - timedelta(minutes=adjust)
        elif adjust_per.lower() == "h":
            dt = dt - timedelta(hours=adjust)
        else:
            raise ValueError("invalid adjustment period. must be 's','m', or 'h'")
        return dt.strftime(fmt)

    @staticmethod
    def _detect_date(d):
        if "published" not in d.keys():
            dx = Entry._alt_pubdate(adjust=75, adjust_per='m')
        else:
            date = d["published"]
            try:
                d = datetime.strptime(date, "%a, %d %b %Y %H:%M %z")
            except:
                try:
                    d = datetime.strptime(date, "%a, %d %b %Y %H:%M %Z")
                except:
                    try:
                        d = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z")
                    except:
                        try:
                            d = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %Z")
                        except:
                            try:
                                d, t = date.split("T")
                                dt = " ".join([d, t[0:11] + t[12:len(t)]])
                                d = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S%z")
                            except:
                                try:
                                    d = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S")
                                except:
                                    dx = Entry._alt_pubdate(adjust=75, adjust_per='m')
                                else:
                                    dx = d.strftime("%Y-%m-%d %H:%M:%S")
                            else:
                                dx = d.strftime("%Y-%m-%d %H:%M:%S")
                        else:
                            dx = d.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        dx = d.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    dx = d.strftime("%Y-%m-%d %H:%M:%S")
            else:
                dx = d.strftime("%Y-%m-%d %H:%M:%S")

        return dx

    def _process_fields(self, d, keys, alts, defaults):

        for key in keys:
            if key in d.keys():
                self.update({key: d[key]})
            elif key in alts.keys():
                if alts[key] in d.keys():
                    self.update({key: d[alts[key]]})
                elif key in defaults.keys():
                    self.update({key: defaults[key]})
                else:
                    self.update({key: None})
            elif key in defaults.keys():
                self.update({key: defaults[key]})
            else:
                self.update({key: None})

        return self

    def restruct(self, raw):
        try:
            self.update({
                "img_loc": Entry._locate_image(d=raw), "pub_datetime": Entry._detect_date(d=raw),
                "summary": self._clean_text(text=raw["summary"].strip())
            })

            self.update({
                "tags": self._tags_parser(d=raw),
                "title": self._clean_text(text=raw["title"]), "selected_count": 0,
                "skipped_count": 0, "template_string": self._build_template_string()
            })

            self._process_fields(d=raw, keys=["author", "url"], alts={"url": "link"},
                                 defaults={"author": "Staff Writer"})
        except KeyError as err:
            print("Error Processing %s" % err, raw)

        else:
            return self

    def __dict__(self):
        return dict(self)


class Feed(object):

    def __init__(self, source, url, section):
        self.source = source
        self.url = url
        self.section = section

    def fetch(self):
        parsed = feedparser.parse(self.url)
        return parsed

    def info(self, parsed):
        return parsed["feed"]

    def entries(self, parsed):
        if "entries" in parsed.keys():

            _entry = Entry(source_name=self.source)
            return [_entry.restruct(ent) for ent in parsed["entries"]]
        else:
            print("No entries found.")
            pass


class Feeds(object):

    def __init__(self, profile):
        if isinstance(profile, Profile):
            self.feeds = profile['feeds']
        else:
            raise TypeError("profile must be a valid user profile instance")

        self.threads = []
        self.page_queue = Queue()

    def downloader(self):
        pass

    def enqueue(self, feed_object):
        pass

    def process(self):
        pass

    def paginate(self, page_size):
        pass
