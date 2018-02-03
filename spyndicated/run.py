# D.Temkin : spyndicated.run (v0.3.1-1) - Copyright LGPLv3 (2018)
import logging
from getpass import getpass
from queue import Queue

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


feedqueue = FeedQueue()

if __name__ == "__main__":
    profile = Profile()
    profile_name = input("Enter Profile Name: ")
    if str(profile_name) == "test":
        profile.load("test")
        user_profile = profile.profile['test']

    else:
        tries = 3
        if str(profile_name) not in profile.names:
            raise ValueError("Invalid Profile Name")
        else:
            if tries >= 1:
                try:
                    profile.load(profile_name, getpass("Password: "))
                    user_profile = profile.profile[profile_name]
                except ValueError:
                    tries -= 1
                    print(ValueError("Invalid Password"))
                else:
                    tries -= 100
            else:
                raise ValueError("Number of tries exceeded!")
    sources = user_profile["sources"]
    for s in range(len(sources)):
        for feed in sources[s]['feeds']:
            f = Feed(source=sources[s], url=feed['url'], section=feed['title'])
            feedqueue.put(f.fetch())

    x = feedqueue.get()
    print(x)
