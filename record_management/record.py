from .rid import RID


class Record:
    def __init__(self, record_id: RID, record_data):
        self.record_id = record_id
        self.record_data = record_data

    def get_id(self):
        return self.record_id

    def get_record_data(self):
        return self.record_data
