import sys
from pathlib import Path

from pandas import DataFrame, read_csv

global yes


def load_file(input_path: str) -> DataFrame:
    """
    Function that loads and cleans file
    :param input_path:
    :return: DataFrame with processes and path to origin file
    """
    with open(input_path, encoding="utf8") as fp:
        data = read_csv(fp, sep=';')
        try:
            data = data.stack().str.replace(',', '.').unstack()
        except AttributeError:
            pass  # nothing to replace
        data = data.fillna(0)
    return data


def calculate_offset(offset) -> float:
    if type(offset) == str:
        time_offset = offset[11:]
        hour_offset = float(time_offset[:2])
        minute_offset = float(time_offset[3:5])
        second_offset = float(time_offset[6:8])
        millisecond_offset = float(time_offset[9:12])
        offset = hour_offset * 3600 + minute_offset * 60 + second_offset + millisecond_offset * 0.001
    return offset


def datetime_shift(date: DataFrame, offset: float):
    """
    This function recalculates time for processes by shifting it on provided amount
    :param date: DataFrame to shift
    :param offset: Amount of time to shift in seconds
    :return: None
    """
    i = 0
    for string in date['Дата Время']:
        if type(string) == str:
            time_point = string[11:]
            hour_point = float(time_point[:2])
            minute_point = float(time_point[3:5])
            second_point = float(time_point[6:8])
            millisecond_point = float(time_point[9:12])

            date.at[i, 'Дата Время'] = hour_point * 3600 + minute_point * 60 + second_point \
                                       + millisecond_point * 0.001 - offset
        elif type(string) == float:
            date.at[i, 'Дата Время'] = float(string) - offset
        i += 1


def check_output(output_path: str) -> bool:
    """
    Function to check if the provided by --output path can be used to write files. If directory not exist then user
    will see the message proposing to create such.
    :param output_path: path to check in string format
    :return: True of False
    """
    if Path(output_path).is_dir():
        return True
    if not Path(output_path).is_dir():
        if yes_no_question('Provided path not exist and will be created'):
            Path(output_path).mkdir(parents=True)
            return True
        else:
            print("Stopped by user")
            return False
    else:
        return False


def get_process_date(data_set: DataFrame) -> str:
    """
    This functions returns the date for provided process using the first cell from column 'Дата Время'
    :param data_set: DataFrame which date should be extracted
    :return: date as string in format dd:mm:yyyy or 1 if date can't be recognized
    """
    process_date = data_set['Дата Время'].iat[0]
    if type(process_date) == str:
        process_date = process_date[:10]
        return process_date
    else:
        return "1"


def save_process(process_data: DataFrame, output: str, start_time: str, previous_date: str, offset: float,
                 p: Path, i: int) -> list:
    """
    Checks process data if exists, checks is --output set and if it can be written, saves
    process in format global_dir/local_dir/file, where local_dir contains process date
    :param process_data:
    :param output:
    :param start_time:
    :param previous_date:
    :param offset:
    :param p:
    :param i:
    :return: last written path with date of previous process or 1 if interrupted by yes_no_question()
    """

    current_date = get_process_date(process_data)

    if not current_date == "1":  # if process has no date
        local_dir_name = 'processes_' + current_date + '_data'
    else:
        local_dir_name = 'offset_processes_data'

    if output:  # deciding final output path considering --output and local folder with date of the process
        if check_output(output):
            output_dir = output + "\\" + str(local_dir_name)
            path_to_return = output
        else:
            print('Output path can\'t be used')
            return ["1"]  # this return will be provided to parse_processes() and function will be interrupted
    else:
        output_dir = str(p.parent) + "\\" + str(local_dir_name)
        path_to_return = str(p.parent)

    if previous_date != current_date:
        i = 1

    try:  # checking if final output exist or may be created
        Path(output_dir).mkdir()
    except FileExistsError:
        if previous_date == current_date:
            pass
        else:
            sys.stdout.write("\n")
            previous_date = current_date
            if not yes_no_question(
                    'Folder with processes "' + output_dir + '" already exist, data will be overwritten'):
                print('Stopped by user')
                return ["1"]  # this return will be provided to parse_processes() and function will be interrupted
    else:
        print("\nSuccessfully created the directory %s " % local_dir_name)

    datetime_shift(process_data, offset)

    process_data.to_csv(output_dir + '\\process_' + str(i) + '_started_at_' +
                        str(start_time[11:][:-4]).replace(":", ".") + '.csv', index=False, sep=';')
    return [path_to_return, previous_date, i]


def yes_no_question(question: str) -> bool:
    global yes
    if yes:
        print(question)
        return True
    else:
        yes = {'yes', 'y', 'ye', ''}
        no = {'no', 'n'}

        print(question + ', continue? [Y/n]')
        choice = input().lower()
        if choice in yes:
            return True
        elif choice in no:
            return False
        else:
            sys.stdout.write("Please respond with 'yes' or 'no'")


def check_input(input_path: str) -> bool:
    if Path(input_path).is_file():
        return True
    else:
        print("Could not read:", input_path)
        return False
