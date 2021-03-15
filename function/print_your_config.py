def print_order_config(config) -> None:
    print(f"*--------------- # ORDER CONFIG # ----------------*")
    for con in config:
        if 'coins_list' in con[0]:
            continue
        print(f"|{con[0]:>35}: {con[1]:>7}     |")
    print(f"*-------------------------------------------------*")
