# D.Temkin : spyndicated.run (v0.3.1-1) - Copyright LGPLv3 (2018)
import logging
from queue import Queue

from spyndicated.plugins import json
from spyndicated.rss.base import Feed
from spyndicated.usr import Profile

logging.basicConfig(level=logging.INFO)


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


q = []
datahand = json.JSONHandler()
datahand.select(identifiers="all")
total_entries = 0
for feed in Profile['feeds']:
    print("Working on feed: %s" % feed['name'])
    f = Feed(name=feed['name'], url=feed['url'])
    print("Fetching Feed")
    x = f.fetch()
    print("Parsing Entries...")
    entries = f.entries(x)
    if entries is False:
        print("None Found! Skipping...")
        pass
    else:
        total_entries += len(entries)
        print("Storing %s entries" % str(len(entries)))
        datahand.insert_multi(records=[dict(entry) for entry in entries])
print("Done. %d entries processed" % total_entries)
