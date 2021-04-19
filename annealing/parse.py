import sys

from function_lib import save_process, load_file, calculate_offset, get_process_date, datetime_shift

"""
Global variables :previous_date: and :current_date: are being used in save_process_output_dir() and parse_processes() to
check if two subsequent processes belongs to the same date. If not - then while checking if dir for new process exists 
the message may be shown to user if he wants to create new directory for it.
"""
previous_date = ""
current_date = ""


def parse_processes(input_path: str, output_path: str) -> None:
    global current_date, previous_date

    [data, p] = load_file(input_path)
    i = 1  # ordinal number of process

    while not data.empty:

        first_non_zero = data['Мощность'].astype(float).ne(0).idxmax()
        heating = data.iloc[first_non_zero:]

        process_start_time = str(data['Дата Время'].iat[first_non_zero])

        first_eq_zero = heating['Мощность'].astype(float).eq(0).idxmin()
        while_process = data.iloc[first_eq_zero:]

        last_process_value = while_process['Мощность'].astype(float).eq(0).idxmax()
        after_process = data.iloc[last_process_value:]

        previous_date = current_date

        offset = calculate_offset(heating.at[0, 'Дата Время'])

        if not after_process['Мощность'].astype(float).eq(0).all():
            last_eq_zero = after_process['Мощность'].astype(float).ne(0).idxmax()
            process = data.iloc[first_non_zero:last_eq_zero]
            datetime_shift(process, offset)
            if i == 1:
                process = process.reset_index(drop=True)  # first may be with zeros at the beginning
            [last_written_path, previous_date] = save_process(process, output_path, process_start_time, previous_date,
                                                              p, i)
            if last_written_path[0] == "1":
                break
        else:
            process = data.iloc[first_non_zero:]
            datetime_shift(process, offset)
            [last_written_path, previous_date] = save_process(process, output_path, process_start_time, previous_date,
                                                              p, i)
            break
        i += 1
        data = data.iloc[last_eq_zero:]
        data = data.reset_index(drop=True)

        sys.stdout.write("\rDone %i processes so far" % i)
        sys.stdout.flush()

    sys.stdout.write('\n' + str(i) + ' files writen to "' + last_written_path[0] + '"')
