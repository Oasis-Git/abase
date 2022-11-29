from .db_info import DbInfo
import pickle
import os
from const import const


class InfoHandle:
    def __init__(self, new_db: bool, db_name):
        self.path = os.getcwd() + '/data'
        if new_db:
            self.db_info = DbInfo(db_name)
        else:
            self.load(db_name)

    def dump(self, db_name):
        outfile = open(self.path + '/' + db_name + '/' + (db_name + const.META_FILE), "wb")
        pickle.dump(self.db_info, outfile)
        outfile.close()

    def load(self, db_name):
        infile = open(self.path + '/' + db_name + '/' + (db_name + const.META_FILE), 'rb')
        self.db_info = pickle.load(infile)
        infile.close()

    def close(self):
        self.dump(self.db_info.name)
