import sys
import argparse
from pathlib import Path
from pandas import read_csv, options

__version__ = 1.1
yes = False
previous_date = ""
current_date = ""

options.mode.chained_assignment = None  # default='warn'


def datetime_parse(date, offset) -> None:
    """
    This function recalculates time for processes by shifting it on provided amount
    :param date: Dataframe to shift
    :param offset: Amount of time to shift
    :return: None
    """
    i = 0
    for string in date['Дата Время']:
        time_point = string[11:]
        hour_point = float(time_point[:2])
        minute_point = float(time_point[3:5])
        second_point = float(time_point[6:8])
        millisecond_point = float(time_point[9:12])

        time_offset = offset[11:]
        hour_offset = float(time_offset[:2])
        minute_offset = float(time_offset[3:5])
        second_offset = float(time_offset[6:8])
        millisecond_offset = float(time_offset[9:12])

        date.at[i, 'Дата Время'] = \
            (hour_point - hour_offset) * 3600 + (minute_point - minute_offset) * 60 + \
            second_point - second_offset + (millisecond_point - millisecond_offset) * 0.001
        i += 1


def get_process_date(data_set) -> str:
    process_date = data_set['Дата Время'].iat[0]
    process_date = process_date[:10]
    return process_date


def save_process_output_dir(process_data, output, p, i) -> str:
    """
    Getting date of current process to save it locally in provided by --output directory or using directory by default
    to save processes consistently by there date start if parsing data for more than one day
    :param process_data: Process dataframe which date should be extruded
    :param output: Optional path from --output
    :param p: Input path to the file. Used to get parent folder to store results by default where input data situated
    :param i: Process number
    :return: true if success
    """

    def check_output(output_path) -> bool:
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

    local_dir_name = 'processes_' + get_process_date(process_data) + '_data'

    if output:  # deciding final output path considering --output and local folder with date of the process
        if check_output(output):
            output_dir = output + "\\" + str(local_dir_name)
            path_to_retun = output
        else:
            print('Output path can\'t be used')
            return "1"
    else:
        output_dir = str(p.parent) + "\\" + str(local_dir_name)
        path_to_retun = str(p.parent)

    global previous_date, current_date

    try:  # checking if final output exist or may be created
        Path(output_dir).mkdir()
    except FileExistsError:
        if previous_date == current_date:
            pass
        else:
            previous_date = current_date
            if not yes_no_question('Folder with processes "' + output_dir + '" already exist, data will be overwritten'):
                print('Stopped by user')
                return "1"
    else:
        print("Successfully created the directory %s " % local_dir_name)

    offset = process_data.at[0, 'Дата Время']
    datetime_parse(process_data, offset)

    process_data.to_csv(output_dir + '\\process_' + str(i) + '_started_at_' +
                        str(offset[11:][:-4]).replace(":", ".") + '.csv', index=False)
    return path_to_retun


def yes_no_question(question) -> bool:
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


def parse_processes(input_path, output_path) -> None:
    global current_date, previous_date
    p = Path(input_path)
    with open(input_path, encoding="utf8") as fp:
        data = read_csv(fp, sep=';')
        data = data.stack().str.replace(',', '.').unstack()
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

                last_path = save_process_output_dir(process, output_path, p, i)
                if last_path == "1":
                    print("Error")
                    break
            else:
                process = data.iloc[first_non_zero:]

                previous_date = current_date
                current_date = get_process_date(process)

                last_path = save_process_output_dir(process, output_path, p, i)
                break
            i += 1
            data = data.iloc[last_eq_zero:]
            data = data.reset_index(drop=True)

            sys.stdout.write("\rDone %i processes so far" % i)
            sys.stdout.flush()

        sys.stdout.write('\n' + str(i) + ' files writen to "' + last_path + '"')


def concat_processes(input, output) -> None:
    print()


def shift_processes(input, output) -> None:
    print()


def check_input(input_path) -> bool:
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

    if not (parse and output_path and concat and shift):  # default action with no flags provided
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
                shift_processes(input_path, output_path)
