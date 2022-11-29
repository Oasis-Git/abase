import sys
import os
import numpy as np

sys.path.append("../..")
sys.path.append("../file_management")
sys.path.append("../record_management")
sys.path.append("../index_management")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from index_management import BPlusTree
from index_management import Index


tree = BPlusTree(4)
"""for i in range(0,2423):
    tree.insert(i, i*2)
#tree.show()
for i in range(12, 687):
    tree.delete(i)
#tree.show()
for i in range(112,143):
    tree.insert(i, i*2)
#tree.show()
print(tree.search(0, 23))"""
"""for i in range(0, 16):
    tree.insert(i, i*2)
for i in range(23, 233):
    tree.delete(i)
for i in range(0,172):
    tree.insert(i,i*2)"""

"""index = Index("2", "2")
for i in range(0, 22):
    index.insert(i, i*2)
for i in range(1, 6):
    index.delete(i)
print(index.search(2,8))
index.dump('./save')"""

index = Index("fds", "fds", empty=False, save_path='./save')
print(index.search(2,100))

