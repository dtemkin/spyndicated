import json
import os

from spyndicated import get_data
from spyndicated.data import BaseHandler


class JSONHandler(BaseHandler):

    def __init__(self, datafile="master.json"):
        super().__init__(loc=get_data(datafile))

    def insert(self, record, duplicates=False):
        jsdata = json.dumps(record) + "\n"
        with open(self.loc, mode="a") as f:
            f.write(jsdata)
            f.flush()


    def select(self, identifiers, n=-1):
        with open(self.loc, "r") as f:
            records = [json.loads(f) for f in f.readlines()]

            if identifiers == "*" or identifiers == "all":
                pass
            elif type(identifiers) is dict:
                for record in records:
                    for k, v in enumerate(identifiers):
                        if self._selector(obj=record, k=k, v=v) is None:
                            records.remove(record)
                        else:
                            pass
            else:
                raise TypeError("Invalid identifiers argument. Must be dict, '*' or 'all'")
        if n == 0:
            return None
        elif n >= 1:
            if n > len(records):
                raise IndexError("invalid n, must be in range -1 to len(records)")
            else:
                return records[0:n]
        elif n == -1:
            return records
        else:
            raise IndexError("invalid n, must be in range -1 to len(records)")

    def insert_multi(self, records, *args, **kwargs):
        duplicates = kwargs.get("duplicates", False)
        with open(self.loc, mode='a') as f:
            if duplicates is False:
                if os.path.isfile(self.loc):
                    sel = self.select(identifiers='all')
                    if len(sel) > 0:
                        curr = [l['title'] for l in sel]
                        f.writelines([json.dumps(record) + "\n" for record in records if record['title'] not in curr])
                    else:
                        f.writelines([json.dumps(record) + "\n" for record in records])
                else:
                    f.writelines([json.dumps(record) for record in records])
            else:
                f.writelines([json.dumps(record) + "\n" for record in records])

    def _selector(self, obj, k, v):
        if k in obj.keys():
            if obj[k] == v:
                return obj
            else:
                return None
        else:
            raise KeyError("Invalid selector.")
