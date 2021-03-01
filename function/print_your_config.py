def print_order_config(config) -> None:
    print(f"*------------ ORDER CONFIG -------------*")
    for con in config:
        print(f"|{con[0]:>20}: {con[1]:>5}            |")

print_order_config([("fewf", "qrrww"), ("123", "435")])