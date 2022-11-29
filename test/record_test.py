import sys
import os
import numpy as np

sys.path.append("../..")
sys.path.append("../file_management")
sys.path.append("../record_management")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from record_management import RCManager
from file_management.bufpagemanager import BufPageManager

manager = RCManager(BufPageManager())
manager.create_file("test", 12)
manager.open_file("test")
handle = manager.handle_helper["test"]
rec = handle.insert_record(np.array([1,2,3],dtype=int))
recc = handle.insert_record(np.array([31,32,33],dtype=int))
print(rec.get_id())
rec = handle.get_record(recc.get_id())
print(rec.get_record_data())
manager.close_file("test")
