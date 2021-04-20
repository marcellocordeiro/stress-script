from colorama import Fore, Style, init


def print_failures(failures, no_stress_runs=1, stress_runs=1, config_size=4):
    init()

    module_colour = Fore.RED
    function_colour = Fore.GREEN

    total_no_stress_failures = 0
    total_stress_failures = 0

    for module in failures:
        print(
            f"==== Failure in module {module_colour}{Style.BRIGHT}{module}{Fore.RESET}{Style.RESET_ALL} ===="
        )

        for test_case in failures[module]:
            print(
                f"{'':<5}> at {function_colour}{Style.BRIGHT}{test_case}{Style.RESET_ALL}"
            )

            function_failures = failures[module][test_case]

            no_stress_failures = 0
            stress_failures = 0
            descriptions = set()

            for failure in function_failures:
                if failure["config"] == "no-stress":
                    total_no_stress_failures += 1
                    no_stress_failures += 1
                else:
                    total_stress_failures += 1
                    stress_failures += 1

                descriptions.add(failure["description"])

            print(f"{'':<7}No stress failures: {no_stress_failures}")
            print(f"{'':<7}Stress failures: {stress_failures}")
            print(f"\n{'':<7}> Descriptions: {Fore.RED}{Style.BRIGHT}")
            for description in descriptions:
                for line in description.split("\n"):
                    print(f"{'':<9}{line}")
                print(Style.RESET_ALL)

    """import json
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(failures, f, ensure_ascii=False, indent=4)"""
