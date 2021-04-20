# Annealing

Script for annealing data analyzing

This script runs through the presented data and separates annealing processes into separate files to make it easier to work with them. Timestamps in each process start with zero and are measuring in seconds.

---

## Usage

To run the script specific flag should be used such as `annealing your/path/to.file [flag]`. You may provide more than one file.

`-p, --parse` or no flags (parsing will run by default)

The script will split the entire sequence into separate CSV files for each process, and recalculate for each of the processing time from zero. The result will be in the same directory as the original file. The processes will be numbered and marked with a start time. 

Processes are parsed by the "Мощность" field by a transition from zero to non-zero value. Thus, the formally supplied power in the "Задание" field but not transferred to the lamps will be ignored. A process is considered a set of dots from the first nonzero occurrence in the "Мощность" field to the next such occurrence, or the end of the file. Thus, cooling is included in the process.

`-s, --shift`

Using this flag you can shift one or more processes on some offset by providing such parameter after flag. Offset considered to be in seconds.

`-c, --concat`

Using this flag while providing more than one file you can concatenate them with time sensing. In the output there will be provided processes with one timeline.

`-o, --output`

With this flag you can provide custom output directory. If no flag provided then input directory will be used by default.

`-y, --yes`

This flag toggles off all yes/no question and they are considered to be positive answered. Yes/no questions are shown to user when directory creation or data overwrite should be confirmed.

`-v, --version`

Will show you the version.

---

While saving script will try to obtain data from process to split information into folders by date. If there is no date provided in column "Дата Время" than all such processes will be stored in the same folder.