import argparse
import sys
from pandas import options

import function_lib
from shift import shift_processes
from concat import concat_processes
from parse import parse_processes
from function_lib import check_input

__version__ = 1.1

options.mode.chained_assignment = None  # default='warn'


def main(self) -> None:
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

    # parser.add_argument(
    #     "--output", "-o",
    #     action="store",
    #     help="custom output path to save results. if not provided input file dir is used by default"
    # )

    # parser.add_argument(
    #     "--concat", "-c",
    #     action="store_true",
    #     help="concat processes in one file with time sensitivity"
    # )

    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="agree and skip all data check yes/no questions such as rewrite data alert and others"
    )

    parser.add_argument(
        "--version", "-v",
        action="version",
        version='%(prog)s ' + str(__version__)
    )

    # parser.add_argument(
    #     "--shift", "-s",
    #     action="store",
    #     type=float,
    #     nargs=1,
    #     help="offset time of processes on certain amount in seconds"
    # )

    args = parser.parse_args()

    input_path = args.path

    function_lib.yes = False
    function_lib.yes = args.yes

    parse = args.parse
    # output_path = args.output
    output_path = ""
    # concat = args.concat
    concat = False
    # shift = args.shift
    shift = None

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
        concat_processes(input_path, output_path)

    if shift:
        for eachpath in input_path:
            if check_input(eachpath):
                shift_processes(eachpath, output_path, shift[0])


if __name__ == '__main__':
    main(sys.argv)
