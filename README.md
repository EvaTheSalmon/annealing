# Annealing

Script for annealing data analyzing

This script runs through the presented data and separates annealing processes into separate files to make it easier to work with them. Timestamps in each process start with zero and are measuring in seconds.

---

## Usage

To run the script specific flag should be used such as `annealing [flag]` .

`-p`

To process the data, a link to the CSV file is sent to the input via the `-p` or `--path` flag. The script will split the entire sequence into separate CSV files for each process, and recalculate for each of the processing time from zero. The result will be in the same directory as the original file. The processes will be numbered and marked with a start time. 

Processes are parsed by the "Мощность" field by a transition from zero to non-zero value. Thus, the formally supplied power in the "Задание" field but not transferred to the lamps will be ignored. A process is considered a set of dots from the first nonzero occurrence in the "Мощность" field to the next such occurrence, or the end of the file. Thus, cooling is included in the process.