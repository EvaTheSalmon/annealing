import sys
import argparse
from pathlib import Path
from pandas import read_csv, options

options.mode.chained_assignment = None  # default='warn'


def datetime_parse(date, offset):
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
    process_date = data_set['Дата Время'].iloc[0]
    process_date = process_date[:10]
    return process_date


def yes_no_question(question) -> bool:
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


def parse_processes(input, output) -> None:
    p = Path(input)
    with open(input, encoding="utf8") as fp:
        data = read_csv(fp, sep=';')
        data = data.stack().str.replace(',', '.').unstack()
        data = data.fillna(0)

        dir_name = 'process_' + get_process_date(
            data) + '_data'  # todo: output processes should be sorted by their date
        output_dir = str(p.parent) + "\\" + str(dir_name)

        try:
            Path(output_dir).mkdir()
        except FileExistsError:
            if not yes_no_question("Process folder already exist, data will be overwritten"):
                print('Stopped by user')
                return
        else:
            print("Successfully created the directory %s " % dir_name)

        i = 1
        while not data.empty:
            first_non_zero = data['Мощность'].astype(float).ne(0).idxmax()

            offset = data['Дата Время'].iloc[first_non_zero]

            heating = data.iloc[first_non_zero:]
            first_eq_zero = heating['Мощность'].astype(float).eq(0).idxmin()
            while_process = data.iloc[first_eq_zero:]
            last_process_value = while_process['Мощность'].astype(float).eq(0).idxmax()
            after_process = data.iloc[last_process_value:]
            if not after_process['Мощность'].astype(float).eq(0).all():
                last_eq_zero = after_process['Мощность'].astype(float).ne(0).idxmax()
                process = data.iloc[first_non_zero:last_eq_zero]

                if i == 1: process = process.reset_index(drop=True)  # first may be with zeros at the beginning

                datetime_parse(process, offset)
                process.to_csv(output_dir + '\\process_' + str(i) + '_started_at_' +
                               str(offset[11:][:-4]).replace(":", ".") + '.csv', index=False)
            else:
                process = data.iloc[first_non_zero:]

                datetime_parse(process, offset)

                process.to_csv(output_dir + '\\process_' + str(i) + '_started_at_' +
                               str(offset[11:][:-4]).replace(":", ".") + '.csv', index=False)
                break
            i += 1
            data = data.iloc[last_eq_zero:]
            data = data.reset_index(drop=True)

            sys.stdout.write("\rDone %i processes so far" % i)
            sys.stdout.flush()

        sys.stdout.write('\n' + str(i) + ' files writen to ' + output_dir)


def concat_processes(input, output) -> None:
    print()


def shift_processes(input, output) -> None:
    print()


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


def main() -> None:
    parser = argparse.ArgumentParser(usage="%(prog)s [options]", description='Tool to process data from\
     annealing machine STE RTA100')
    parser.add_argument(
        "path", metavar='/path/to/your.file', type=str, nargs='+',
        help="path to '.csv' files to extract data to work with"
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
        "--shift", "-s",
        action="store_true",
        help="offset time of processes on certain amount in seconds"
    )

    args = parser.parse_args()

    path = args.path[0]
    print(path)

    if not Path(path).is_file():
        print("Could not read:", path)
        return

    parse = args.parse
    output = args.output
    concat = args.concat
    shift = args.shift

    if output:
        if not check_output(output):
            print('Output path can\'t be used')
            return

    if not (parse and output and concat and shift):  # default action with no flags provided
        parse_processes(path, output)
    if parse:
        parse_processes(path, output)
    if concat:
        concat_processes(path, output)
    if shift:
        shift_processes(path, output)