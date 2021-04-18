import sys
import argparse
from pathlib import Path

from pandas import read_csv, options, DataFrame

__version__ = 1.1
yes = False

previous_date = ""
current_date = ""
"""
Global variables :previous_date: and :current_date: are being used in save_process_output_dir() and parse_processes() to
check if two subsequent processes belongs to the same date. If not - then while checking if dir for new process exists 
the message may be shown to user if he wants to create new directory for it.
"""

options.mode.chained_assignment = None  # default='warn'


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

            date.at[i, 'Дата Время'] = hour_point * 3600 + minute_point * 60 + second_point + \
                                   millisecond_point * 0.001 - offset
        elif type(string) == float:
            date.at[i, 'Дата Время'] = float(string) - offset
        i += 1


def get_process_date(data_set: DataFrame) -> str:
    """
    This functions returns the date for provided process using the first cell from column 'Дата Время'
    :param data_set: DataFrame which date should be extracted
    :return: date as string in format dd:mm:yyyy
    """
    process_date = data_set['Дата Время'].iat[0]
    if type(process_date) == str:
        process_date = process_date[:10]
        return process_date
    else:
        return "1"


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


def save_process_output_dir(process_data: DataFrame, output: str, start_time: str, offset: float, p: Path, i: int) -> str:
    """
    Getting date of current process to save it locally in provided by --output directory or using directory by default
    to save processes consistently by there date start if parsing data for more than one day
    :param process_data: Process dataframe which date should be extruded
    :param output: Optional path from --output
    :param start_time: Time of process start
    :param offset: Offset in seconds to shift time in datetime_shift()
    :param p: Input path to the file. Used to get parent folder to store results by default where input data situated
    :param i: Process serial number
    :return: Directory where all files were put. It may be --output or default
    """

    if not get_process_date(process_data) == "1":
        local_dir_name = 'processes_' + get_process_date(process_data) + '_data'
    else:
        local_dir_name = 'offsetted_processes_' + str(i) + '_data'

    if output:  # deciding final output path considering --output and local folder with date of the process
        if check_output(output):
            output_dir = output + "\\" + str(local_dir_name)
            path_to_return = output
        else:
            print('Output path can\'t be used')
            return "1"  # this return will be provided to parse_processes() and function will be interrupted
    else:
        output_dir = str(p.parent) + "\\" + str(local_dir_name)
        path_to_return = str(p.parent)

    global previous_date, current_date

    try:  # checking if final output exist or may be created
        Path(output_dir).mkdir()
    except FileExistsError:
        if previous_date == current_date:
            pass
        else:
            previous_date = current_date
            if not yes_no_question(
                    'Folder with processes "' + output_dir + '" already exist, data will be overwritten'):
                print('Stopped by user')
                return "1"  # this return will be provided to parse_processes() and function will be interrupted
    else:
        print("\nSuccessfully created the directory %s " % local_dir_name)

    datetime_shift(process_data, offset)

    process_data.to_csv(output_dir + '\\process_' + str(i) + '_started_at_' +
                        str(start_time[11:][:-4]).replace(":", ".") + '.csv', index=False, sep=';')
    return path_to_return


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


def parse_processes(input_path: str, output_path: str) -> None:
    global current_date, previous_date

    p = Path(input_path)
    with open(input_path, encoding="utf8") as fp:
        data = read_csv(fp, sep=';')
        try:
            data = data.stack().str.replace(',', '.').unstack()
        except AttributeError:
            pass  # nothing to replace
        data = data.fillna(0)

        i = 1
        current_date = ""
        last_path = ""

        while not data.empty:
            first_non_zero = data['Мощность'].astype(float).ne(0).idxmax()

            heating = data.iloc[first_non_zero:]
            first_eq_zero = heating['Мощность'].astype(float).eq(0).idxmin()
            while_process = data.iloc[first_eq_zero:]
            last_process_value = while_process['Мощность'].astype(float).eq(0).idxmax()
            after_process = data.iloc[last_process_value:]
            if not after_process['Мощность'].astype(float).eq(0).all():
                last_eq_zero = after_process['Мощность'].astype(float).ne(0).idxmax()
                process = data.iloc[first_non_zero:last_eq_zero]

                if i == 1:
                    process = process.reset_index(drop=True)  # first may be with zeros at the beginning

                previous_date = current_date
                current_date = get_process_date(process)

                offset = process.at[0, 'Дата Время']

                if type(offset) == str:  # todo need to be shorten and reduce redundancy
                    time_offset = offset[11:]
                    hour_offset = float(time_offset[:2])
                    minute_offset = float(time_offset[3:5])
                    second_offset = float(time_offset[6:8])
                    millisecond_offset = float(time_offset[9:12])
                    offset = hour_offset * 3600 + minute_offset * 60 + second_offset + millisecond_offset * 0.001

                process_start_time = str(data['Дата Время'].iat[first_non_zero])

                last_path = save_process_output_dir(process, output_path, process_start_time, offset, p, i)
                if last_path == "1":
                    print("Error")
                    break
            else:
                process = data.iloc[first_non_zero:]

                previous_date = current_date
                current_date = get_process_date(process)

                offset = process.at[0, 'Дата Время']

                if type(offset) == str:
                    time_offset = offset[11:]
                    hour_offset = float(time_offset[:2])
                    minute_offset = float(time_offset[3:5])
                    second_offset = float(time_offset[6:8])
                    millisecond_offset = float(time_offset[9:12])
                    offset = hour_offset * 3600 + minute_offset * 60 + second_offset + millisecond_offset * 0.001

                process_start_time = str(data['Дата Время'].iat[first_non_zero])

                last_path = save_process_output_dir(process, output_path, process_start_time, offset, p, i)
                break
            i += 1
            data = data.iloc[last_eq_zero:]
            data = data.reset_index(drop=True)

            sys.stdout.write("\rDone %i processes so far" % i)
            sys.stdout.flush()

        sys.stdout.write('\n' + str(i) + ' files writen to "' + last_path + '"')


def concat_processes(input, output) -> None:
    print()


def shift_processes(input_path: str, output: str, shift: float) -> str:
    p = Path(input_path)
    with open(input_path, encoding="utf8") as fp:
        data = read_csv(fp, sep=';')
        try:
            data = data.stack().str.replace(',', '.').unstack()
        except AttributeError:
            pass  # nothing to replace
        data = data.fillna(0)

    if output:  # deciding final output path considering --output and local folder with date of the process
        if check_output(output):
            output_dir = output
        else:
            print('Output path can\'t be used')
            return "1"  # this return will be provided to parse_processes() and function will be interrupted
    else:
        output_dir = str(p.parent)

    datetime_shift(data, shift)

    if Path(output_dir + '\\shifted_'+p.name).is_file():
        if yes_no_question('File already exists, data will overwritten'):
            data.to_csv(output_dir + '\\shifted_'+p.name, index=False)
            sys.stdout.write("Data written to " + output_dir)
            sys.stdout.flush()
        else:
            print('Stopped by user')
            return "1"
    else:
        data.to_csv(output_dir + '\\shifted_'+p.name, index=False)
        sys.stdout.write("Data written to " + output_dir)
        sys.stdout.flush()


def check_input(input_path: str) -> bool:
    if Path(input_path).is_file():
        return True
    else:
        print("Could not read:", input_path)
        return False


def main() -> None:
    parser = argparse.ArgumentParser(usage="%(prog)s [options]", description='This is a tool to process data from\
     annealing machine STE RTA100')
    parser.add_argument(
        "path", metavar='/path/to/your.file', type=str, nargs='+',
        help="input path to '.csv' files to extract data to work with"
    )

    parser.add_argument(
        "--parse", "-p",
        action="store_true",
        help="search data for processes and split them in separate files\
             with time offsetting to zero (used by default if no flags specified)"
    )

    parser.add_argument(
        "--output", "-o",
        action="store",
        help="custom output path to save results. if not provided input file dir is used by default"
    )

    parser.add_argument(
        "--concat", "-c",
        action="store_true",
        help="concat processes in one file with time sensitivity"
    )

    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="agree and skip all data check yes/no questions such as rewrite data alert and others"
    )

    parser.add_argument(
        "--shift", "-s",
        action="store",
        type=float,
        nargs=1,
        help="offset time of processes on certain amount in seconds"
    )

    args = parser.parse_args()

    input_path = args.path

    global yes
    yes = False
    yes = args.yes

    parse = args.parse
    output_path = args.output
    concat = args.concat
    shift = args.shift

    # default action with no flags provided
    if parse is False and concat is False and shift is None:
        for eachpath in input_path:
            if check_input(eachpath):
                parse_processes(eachpath, output_path)
    elif parse:
        for eachpath in input_path:
            if check_input(eachpath):
                parse_processes(eachpath, output_path)

    if concat:
        if input_path.count() > 2:
            for eachpath in input_path:
                if check_input(eachpath):
                    concat_processes(eachpath, output_path)
        else:
            print('You can concat only more than one file')
            return
    if shift:
        for eachpath in input_path:
            if check_input(eachpath):
                shift_processes(eachpath, output_path, shift[0])
