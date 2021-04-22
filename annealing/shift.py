import sys

from function_lib import datetime_shift, load_file, save_process
from pathlib import Path


def shift_processes(input_path: str, output_path: str, shift: float) -> str:
    data = load_file(input_path)
    p = Path(input_path)

    first_non_zero = data['Мощность'].astype(float).ne(0).idxmax()
    process_start_time = str(data['Дата Время'].iat[first_non_zero])

    last_written_path = save_process(data, output_path, process_start_time, "1", shift,
                                     p, 0)
    sys.stdout.write("Data written to " + last_written_path[0])
    sys.stdout.flush()
