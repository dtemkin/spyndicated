# D.Temkin : spyndicated.utils.mysql_conn (v0.3.1-1) - Copyright LGPLv3 (2018)

from string import Formatter

from mysql.connector import connection, connect, Error as sqlerr, errorcode as sqlerr_code


class Database(object):

    def __init__(self, **kwargs):
        self.config = {
            "database": kwargs.get("database", "spyndicated"), "user": kwargs.get("username", "root"),
            "password": kwargs.get("password", "yo2ek4f33"), "host": kwargs.get("host", "localhost"),
            "port": kwargs.get("port", "3306")
        }
        self.fmt = Formatter()

    def test_connect(self):
        try:
            cnx = connect(**self.config)
        except sqlerr as err:
            if err.errno == sqlerr_code.ER_ACCESS_DENIED_ERROR:
                print(sqlerr_code.ER_ACCESS_DENIED_ERROR(
                        "Uh-oh something went wrong. It seems you username and/or password is invalid"))
                return False
            elif err.errno == sqlerr_code.ER_ACCESS_DENIED_NO_PASSWORD_ERROR:
                print(sqlerr_code.ER_ACCESS_DENIED_NO_PASSWORD_ERROR("Oops! No password supplied to config"))
                return False
            elif err.errno == sqlerr_code.ER_BAD_DB_ERROR:
                print(sqlerr_code.ER_BAD_DB_ERROR("Oops! it seems that the database specified does not exist"))
                return False
            else:
                print(err)
                return False
        else:
            cnx.close()
            return True

    def connect(self):
        try:
            cnx = connection.MySQLConnection(**self.config)
        except sqlerr as err:
            raise Exception(err)
        else:
            return cnx.connect(), cnx.cursor()

    def _db_struct(self, get):
        _tables = {
            'entries': ["eid", "fid", "sid", "url", "title",
                        "pub_datetime", "age", "author", "summary",
                        "template_string", "curr_rank", "prev_rank",
                        "chg_rank", "pctchg_rank", "selected_count",
                        "skipped_count", "img_loc", "source_name",
                        "feed_section"],
            'entry_topics': ["e_topid", "eid", "fid", "topic", "prob"],
            'feed_topics': ["f_topid", "fid", "topic", "prob"],
            'feeds': ["fid", "sid", "section", "url"],
            'sources': ["sid", "name"],
            'tags': ["tagid", "eid", "fid", "tag", "prob"]
        }

        _views = {
            'preferred_entries_list': [],
            'selected_entries_list': [],
            'skipped_entries_list': []
        }

        if get == "tables":
            return _tables.keys()
        elif get in _tables.keys():
            return _tables[get]
        elif get == "views":
            return _views.keys()
        elif get in _views.keys():
            return _views[get]
        else:
            raise KeyError("Invalid db item, not found in db structure.")

    def _check_cols(self, table, target_cols):
        valid_cols = self._db_struct(get=table)
        diffs = [i for i in target_cols if i not in valid_cols]
        if len(diffs) > 0:
            raise KeyError("Invalid columns! %s" % diffs)
        else:
            return target_cols
