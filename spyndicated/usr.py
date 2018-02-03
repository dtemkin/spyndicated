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


class Profile(object):

    def __init__(self):
        self.readable_file = open(get_config('profiles.yaml'), mode='r')
        self.appendable_file = open(get_config("profiles.yaml"), mode='a')

        self.profiles = yaml.load(self.readable_file)['profiles']
        self.profile = {}

    def load(self, username, password=None):
        if password is None:
            self.profile.update({username: self.profiles["('%s', null)" % username]})

        else:
            try:
                pro = self.profiles["('%s', %s)" % (username, password)]
            except ValueError:
                raise ValueError("Invalid Profile Credentials")
            else:
                self.profile.update({username: pro})

    def create(self):
        pass

    def edit(self, prefs):
        pass

    def _model_detect(self):
        pass

    def _set_preferences(self):
        pass

    def setup(self):
        pass

    @property
    def names(self):
        return [i[0] for i in self.profiles.keys()]
