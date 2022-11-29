from .result import Result


def print_by_type(result: Result):
    if result.form == 0:
        if result.run_time:
            print(result.msg + f' in {result.run_time} sec')
        else:
            print(result.msg)
    elif result.form == 1:
        print("done")
        print('+----------------------------+')
        print('| Tables_in_database         |')
        print('+----------------------------+')
        for item in result.msg:
            print('| ' + item + ' '*(26 - len(item)) + ' |')
        print(f'{len(result.msg)} rows in set ({result.run_time} sec)')


def print_all(result_list: list[Result]):
    for result in result_list:
        print_by_type(result)

