class RID:
    def __init__(self, page_id, slot_id):
        self.page_id = page_id
        self.slot_id = slot_id

    def __str__(self):
        return f'{{page_id: {self.page_id}, slot_id: {self.slot_id}}}'

    def get_page_id(self):
        return self.page_id

    def get_slot_id(self):
        return self.slot_id

    def to_string(self):
        return str(self.page_id) + '_' + str(self.slot_id)
