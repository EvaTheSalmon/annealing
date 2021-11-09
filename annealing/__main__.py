import argparse
import sys
from io import open
import csv

__version__ = 1.2


class Process:

    def __init__(self) -> None:
        pass

    @staticmethod
    def _parse(path: str):
        with open(path, "r", encoding="utf-8-sig") as processfile:
            process = csv.reader(processfile, delimiter=";")

            headers = next(process)
            date_id = headers.index('Дата Время')
            temp_id = headers.index('Температура')
            powr_id = headers.index('Мощность')

            heating_process = []
            heating_process += ['Time', 'Temp', 'Power']

            heating_flag = 0
            cooling_flag = 0

            for row in process:

                powr = row[powr_id].split(",", 1)[0]
                temp = row[temp_id].split(",", 1)[0]
                date = row[date_id].split(" ", 1)[1]

                if powr != 0 and heating_flag == 0:
                    heating_flag = 1
                    cooling_flag = 0

                    heating_process += [date, temp, date]

                    if heating_process:
                        with open('names.csv', 'w', newline='\r\n', encoding='utf-8-sig') as csvfile:
                            writer = csv.writer(csvfile)
                            # todo better to write line on every read without even heating process stored

                if heating_flag == 1:
                    heating_process += [date, temp, date]

                if heating_flag == 1 and powr == 0:
                    cooling_flag = 1
                    heating_flag = 0

                    heating_process += [date, temp, date]

                if cooling_flag == 1:
                    heating_process += [date, temp, date]


def main(self) -> None:
    parser = argparse.ArgumentParser(usage="%(prog)s [options]", description='This is a tool to process data from\
     annealing machine STE RTA100')
    parser.add_argument(
        "path", metavar='/path/to/your.file', type=str, nargs='+',
        help="input path to '.csv' files to extract data to work with"
    )

    args = parser.parse_args()
    input_file = args.path
    process = Process()

    for eachfile in input_file:
        process._parse(eachfile)


if __name__ == '__main__':
    main(sys.argv)
