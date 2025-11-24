from custom_lib.flag_pkg import FlagPkg

def flag_sync_process(flag_pkg_dict: dict[str, FlagPkg], 
                      sync_list: list[FlagPkg]):
    while True:
        for target_process_name in sync_list[1:]:
            if flag_pkg_dict[sync_list[0]].enable.is_set():
                flag_pkg_dict[target_process_name].enable.set()
            else:
                flag_pkg_dict[target_process_name].enable.clear()
                
            if flag_pkg_dict[sync_list[0]].complete.is_set():
                flag_pkg_dict[target_process_name].complete.set()
            else:
                flag_pkg_dict[target_process_name].complete.clear()
                
            if flag_pkg_dict[sync_list[0]].error.is_set():
                flag_pkg_dict[target_process_name].error.set()
            else:
                flag_pkg_dict[target_process_name].error.clear()