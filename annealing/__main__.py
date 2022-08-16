import argparse
import sys
from io import open
import csv
from os import path

__version__ = 1.2


class Process:

    def __init__(self) -> None:
        pass

    @staticmethod
    def _parse(path: str, output_path: str):

        with open(path, "r", encoding="utf-8-sig") as processfile:
            series = csv.reader(processfile, delimiter=";")
            header = next(series)

            date_id = header.index('Дата Время')
            temp_id = header.index('Температура')
            powr_id = header.index('Мощность')

            heating_and_cooling = []
            heating_and_cooling.append(['Дата Время', 'Температура', 'Мощность'])

            powr_prev = -1
            i = 1

            for row in series:

                try:
                    powr = int(row[powr_id].split(",", 1)[0])
                except ValueError:
                    powr = 0
                
                temp = row[temp_id].split(",", 1)[0]
                date = row[date_id].split(" ", 1)[1]
                
                heating_and_cooling.append([date, temp, powr])
                
                if powr != 0 and powr_prev == 0:

                    with open(output_path + "/" + "proc_of_" + str(path.split("\\")[-1]).split(".csv")[0] + "_at_" + str(date[:8]).replace(":","_") + ".csv", "w", encoding="utf-8-sig", newline='') as heating_and_cooling_file:
                        writer = csv.writer(heating_and_cooling_file, delimiter=";")
                        writer.writerows(heating_and_cooling)

                    heating_and_cooling.clear()
                    heating_and_cooling.append(['Дата Время', 'Температура', 'Мощность'])
                    i+=1
                
                powr_prev = powr
                    
    

def main(self) -> None:

    parser = argparse.ArgumentParser(usage="%(prog)s [options]", description='This is a tool to process data from\
     annealing machine STE RTA100')

    parser.add_argument(
        "path", metavar='/path/to/your.file', type=str, nargs='+',
        help="input path to '.csv' files to extract data to work with"
    )
    parser.add_argument(
        "--output", "-o",
        action="store",
        help="custom output path to save results, if not provided input file dir is used by default"
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version='%(prog)s ' + str(__version__)
    )

    output_path = "."

    args = parser.parse_args()
    input_file = args.path
    output_path = args.output if args.output else "."

    if output_path and path.isdir(str(output_path)):
        process = Process()
        for eachfile in input_file:
            process._parse(eachfile, output_path)
    else:
         print("Given output path: " + str(output_path) + " does not exist")

if __name__ == '__main__':
    main(sys.argv)
