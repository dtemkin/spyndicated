# D.Temkin : spyndicated.run (v0.3.1-1) - Copyright LGPLv3 (2018)
import logging
from queue import Queue
from time import sleep

from spyndicated.plugins import json
from spyndicated.rss.base import Feed
from spyndicated.usr import Profile

logging.basicConfig(level=logging.INFO)
datahand = json.JSONHandler()

def _check_first_run():
    # Create Initial Profile
    pass



class FeedQueue(Queue):
    _stop = False

    def __init__(self):
        super().__init__()

    def close(self):
        self._stop = True

    def __iter__(self):
        while True:
            feed_data = self.get()
            try:
                if self._stop is True:
                    return
                yield feed_data
            finally:
                self.task_done()


def update_all():
    total_entries = 0
    for feed in Profile['feeds']:
        selected = datahand.select(identifiers="all")
        print("Working on feed: %s" % feed['name'])
        f = Feed(name=feed['name'], url=feed['url'], is_blog=feed['is_oped_blog'])
        print("Fetching Feed")
        x = f.fetch()
        print("Parsing Entries...")
        entries = f.entries(x)
        if entries is False:
            print("None Found! Skipping...")
            pass
        else:
            records = [dict(entry) for entry in entries if
                       dict(entry)['title'] not in [sel['title'] for sel in selected]]
            print("Storing %s entries" % str(len(records)))
            total_entries += len(records)
            datahand.insert_multi(records=records)
    print("Done. %d entries processed" % total_entries)


if __name__ in "__main__":
    while True:
        update_all()
        sleep(3600)
