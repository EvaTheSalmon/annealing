# Annealing

Script for Semiteq RTA100 data analyzing

![](http://www.semiteq.ru/images/cms/data/prod/ste_rta100.jpg)

This script runs through the presented data and cuts annealing processes into separate files to make it easier to work with them. Timestamps in each process start with zero and are measuring in seconds.

---

## Usage

To run the script specific flag should be used such as `annealing your/path/to.file [flag]`. You may provide more than one file.

`-p, --parse` or no flags (parsing will run by default)

The script will split the entire sequence into separate CSV files for each process, and recalculate for each of the processing time from zero. The result will be in the same directory as the original file. The processes will be numbered and marked with a start time.

Processes are parsed by the "Мощность" field by a transition from zero to non-zero value. Thus, the formally supplied power in the "Задание" field but not transferred to the lamps will be ignored. A process is considered a set of dots from the first nonzero occurrence in the "Мощность" field to the next such occurrence, or the end of the file. Thus, cooling is included in the process.

`-o, --output`

With this flag, you can provide a custom output directory. If no flag provided then the input directory will be used by default.

`-v, --version`

Will show you the version.