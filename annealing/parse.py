import sys

from function_lib import save_process, load_file, calculate_offset
from pathlib import Path


def parse_processes(input_path: str, output_path: str) -> None:
    data = load_file(input_path)
    p = Path(input_path)
    i = 1  # ordinal number of process

    previous_date = ""
    current_date = ""
    last_written_path = ""

    while not data.empty:

        first_non_zero = data['Мощность'].astype(float).ne(0).idxmax()
        heating = data.iloc[first_non_zero:]

        process_start_time = str(data['Дата Время'].iat[first_non_zero])

        first_eq_zero = heating['Мощность'].astype(float).eq(0).idxmin()
        while_process = data.iloc[first_eq_zero:]

        last_process_value = while_process['Мощность'].astype(float).eq(0).idxmax()
        after_process = data.iloc[last_process_value:]

        offset = calculate_offset(heating.at[first_non_zero, 'Дата Время'])

        current_date = previous_date

        if not after_process['Мощность'].astype(float).eq(0).all():

            last_eq_zero = after_process['Мощность'].astype(float).ne(0).idxmax()
            process = data.iloc[first_non_zero:last_eq_zero]
            if i == 1:
                process = process.reset_index(drop=True)
            [last_written_path, previous_date] = save_process(process, output_path, process_start_time, current_date,
                                                              offset, p, i)

            if last_written_path == "1":
                break
        else:
            process = data.iloc[first_non_zero:]
            [last_written_path, previous_date] = save_process(process, output_path, process_start_time, current_date,
                                                              offset, p, i)
            break
        i += 1
        data = data.iloc[last_eq_zero:]
        data = data.reset_index(drop=True)

        sys.stdout.write("\rDone %i processes so far" % i)
        sys.stdout.flush()

    sys.stdout.write('\n' + str(i) + ' files writen to "' + last_written_path + '"')
