def concat_processes(input_path: list, output_path: str) -> None:
    main_data = DataFrame
    for each_file in input_path:
        p = Path(each_file)
        with open(each_file, encoding="utf8") as fp:
            data = read_csv(fp, sep=';')
        try:
            data = data.stack().str.replace(',', '.').unstack()
        except AttributeError:
            pass  # nothing to replace
        data = data.fillna(0)
        concat(main_data, data)
    print(main_data )