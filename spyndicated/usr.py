import yaml
from simplecrypt import decrypt, encrypt

from spyndicated import get_config


def _decrypt_key(uname, pwd):
    with open("%s.enc" % uname, mode='r') as f:
        try:
            dec = decrypt(password=pwd, data=f.read())
        except Exception as err:
            raise Exception(err)
        else:
            return dec


def _encrypt_key(uname, pwd):
    with open("%s.enc" % uname, mode='w') as f:
        try:
            enc = encrypt(pwd, "VALID PASSWORD")
        except Exception as err:
            raise Exception(err)
        else:
            f.write(enc)


Profile = yaml.load(open(get_config("profiles.yaml"), mode='r'))

#
# class Profile(object):
#
#     def __init__(self):
#         self.file = get_config("profiles.yaml")
#         self.profiles = {}
#
#     def load(self):
#         return yaml.load(open(self.file, mode='r'))
#
#     def create(self):
#         pass
#
#     def add_feed(self, source, title, url, feed_update_cycle=1440):
#         feeds = self.profiles['feeds']
#         feed  = {"id": len(feeds), "source": source, "title": title,
#                  "feed_update_cycle": feed_update_cycle,
#                  "url": url, "last_updated": None,
#                  "lda_topics_wts":{}}
#         feeds.append(feed)
#         self.profiles.update({"feeds": feeds})
#
#     def save(self):
#         for profile in self.profiles:
#             if profile['name'] == self.profile['name']:
#                 self.profiles.remove(profile)
#         self.profiles.append(self.profile)
#         yaml.dump(self.profiles, open(self.file, mode='w'))
#
#
#     def edit(self, prefs):
#         pass
#
#     def _model_detect(self):
#         pass
#
#     def _set_preferences(self):
#         pass
#
#     def setup(self):
#         pass
