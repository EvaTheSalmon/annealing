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

                    with open("proc_of_" + str(path.split("\\")[-1]).split(".csv")[0] + "_at_" + str(date[:8]).replace(":","_") + ".csv", "w", encoding="utf-8-sig", newline='') as heating_and_cooling_file:
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

    args = parser.parse_args()
    input_file = args.path
    process = Process()

    for eachfile in input_file:
        process._parse(eachfile)


if __name__ == '__main__':
    main(sys.argv)
