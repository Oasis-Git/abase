# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import os
import stat
from system_management import *


def main():
    system_manager = SystemManager()
    sql = ''
    mode = os.fstat(0).st_mode
    while True:
        if not stat.S_ISREG(mode):
            # if stdin is redirected, do not print prefix
            if system_manager.database_using():
                prefix = f'aBase({system_manager.database_using()})'
            else:
                prefix = f'aBase()'
            print(('-'.rjust(len(prefix)) if sql else prefix) + '> ', end='')
        try:
            sql += ' ' + input()
        except (KeyboardInterrupt, EOFError):
            break
        if sql.strip().lower() in ('quit', 'exit', '.quit', '.exit'):
            system_manager.close()
            break
        if sql.endswith(';'):
            output = system_manager.execute(sql)
            print_all(output)
            sql = ''


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
