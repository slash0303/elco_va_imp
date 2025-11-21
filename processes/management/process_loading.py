from custom_lib.flag_pkg import FlagPkg
from custom_lib.eaxtension import LogE
import time

def manage_process_loading_process(flag_pkg_dict: dict[str, FlagPkg]):
    timer_dict = {}
    for process_name in flag_pkg_dict.keys():
        timer_dict[process_name] = {"running": True, "time": time.time()}

    while True:
        all_set = True
        for process_name, flag_pkg in flag_pkg_dict.items():
            if timer_dict[process_name]["running"] and flag_pkg.loaded.is_set():
                timer_dict[process_name]["time"] = time.time() - timer_dict[process_name]["time"]
                timer_dict[process_name]["running"] = False

            all_set = all_set and flag_pkg.loaded.is_set()

        if all_set:
            for process_name, timer in timer_dict.items():
                LogE.d(process_name, f'{timer["time"]} elapsed.')
            # do something
            break
        else:
            print("loading...", end="\r")