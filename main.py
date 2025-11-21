# Std lib (multiprocessing)
from multiprocessing import Process, Event, Manager

# Std lib (etc.)
import inspect

# Custom lib (multiprocessing)
from processes.audio.audio_stream import audio_stream_process
from processes.activation.vad.voice_detection import voice_detection_process
from processes.activation.gaze.gaze_detection import gaze_detection_process
from processes.stt.transcription import transcription_process
from processes.llm.get_response import get_response_process
from processes.tts.speech_synthesis import speech_synthesis_process
from processes.management.process_loading import manage_process_loading_process

# Custom lib (etc.)
from custom_lib.eaxtension import LogE
from custom_lib.flag_pkg import FlagPkg


class ProcessInfo:
    flag_pkg_dict = {}

    def __init__(self, func, args: list):
        self.func = func
        self.func_name = func.__name__
        sig = inspect.signature(func)
        self.func_params = sig.parameters.values()
        flag_pkg = FlagPkg(self.func_name)
        self.args = tuple([flag_pkg] + args)
        
        if len(self.func_params) != len(self.args):
            err_msg = f"Count of process arguments aren't matched({self.func_name}).(required: {len(self.func_params)}, given: {len(self.args)})"
            raise AttributeError(err_msg)
        
        ProcessInfo.flag_pkg_dict[self.func_name] = flag_pkg


DEBUG_FLAGS = {
    "process_param": True
}

if __name__ == "__main__":
    PROCESS_NAME = "main"

    val = "1"

    # TODO: shm 생성

    process_info_list = [
        ProcessInfo(audio_stream_process, []),
        ProcessInfo(voice_detection_process, []),
        ProcessInfo(gaze_detection_process, []),
        ProcessInfo(transcription_process, []),
        ProcessInfo(get_response_process, []),
        ProcessInfo(speech_synthesis_process, [val])
    ]

    if DEBUG_FLAGS["process_param"]:
        for process_info in process_info_list:
            print(f"<{process_info.func_name}>")
            if len(process_info.args) == 0:
                print("This function doesn't have any params")
                print("-------------------------------------------")
                continue
            for process_param, process_arg in zip(process_info.func_params, process_info.args):
                print(f"{process_param}: {process_arg}")
            print("-------------------------------------------")

    for flag_pkg in ProcessInfo.flag_pkg_dict.values():
        flag_pkg.loading.set()

    process_list = []
    for process_info in process_info_list:
        process = Process(target=process_info.func,
                          args=process_info.args,
                          name=process_info.func_name)
        process.start()
        process.join()
        process_list.append(process)
        LogE.d(PROCESS_NAME, f"{process.name} started")


    process = Process(target=manage_process_loading_process,
                      args=(ProcessInfo.flag_pkg_dict,))
    process.start()
    process.join()