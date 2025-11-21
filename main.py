# Std lib (multiprocessing)
from multiprocessing import Process, Event, Manager

# Std lib (etc.)

# Custom lib (multiprocessing)
from processes.audio.audio_stream import audio_stream_process
from processes.vad.voice_detection import voice_detection_process
from processes.llm.get_response import get_response_process

# Custom lib (etc.)
from eaxtension import LogE

class ProcessInfo:
    def __init__(self, func, args: list):
        if func.__code__.co_argcount != len(args):
            raise ReferenceError(f"Process argument count doesn't match.(required: {func.__code__.co_argcount}, given: {len(args)})")
        self.name = func
        self.args = args

if __name__ == "__main__":
    PROCESS_NAME = "main"

    process_info_list = [
        ProcessInfo(audio_stream_process, []),
        ProcessInfo(voice_detection_process, []),
        ProcessInfo(get_response_process, [])
    ]

    process_list = []
    for process_info in process_info_list:
        process = Process(process_info.process)
        process.start()
        process.join()
        process_list.append(process)
        LogE.d(PROCESS_NAME, f"{process.name} started")