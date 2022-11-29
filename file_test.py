import os
import stat
from system_management import *


def test():
    system_manager = SystemManager()
    with open('./final/partsupp.txt') as f:
        lines = f.readlines()
        for i in lines:
            output = system_manager.execute(i)
            print_all(output)
        system_manager.close()
    print("Done")


test()
