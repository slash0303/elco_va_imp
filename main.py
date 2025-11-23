# Std lib (multiprocessing)
from multiprocessing import Process, Event, Manager
from multiprocessing import shared_memory

# Std lib (etc.)
import inspect
import time
import sys

# Custom lib (multiprocessing)
from processes.audio.audio_stream import audio_stream_process
from processes.activation.vad.voice_detection import voice_detection_process
from processes.activation.gaze.gaze_detection import gaze_detection_process
from processes.stt.transcription import transcription_process
from processes.llm.get_response import get_response_process
from processes.tts.speech_synthesis import speech_synthesis_process
from processes.management.process_loading import manage_process_loading_process
from processes.management.state_manage import manage_state_process

# Custom lib (etc.)
from custom_lib.eaxtension import LogE
from custom_lib.flag_pkg import FlagPkg
import custom_lib.global_constants as gc 

import numpy as np


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
        
        # Flag pkg applying
        if self.func_name == "gaze_detection_process":      # use same flag pkg
            ProcessInfo.flag_pkg_dict[self.func_name] = ProcessInfo.flag_pkg_dict["voice_detection_process"]
        else:
            ProcessInfo.flag_pkg_dict[self.func_name] = flag_pkg



DEBUG_FLAGS = {
    "process_param": True
}

if __name__ == "__main__":
    PROCESS_NAME = "main"

    gazing_flag = Event()

    audio_stream_readable_flag = Event()
    vad_stream_read_flag = Event()
    vad_stream_read_flag.set()

    # TODO: shm 생성
    audio_stream_shm = shared_memory.SharedMemory(create=True, 
													size=np.zeros(gc.audio.FRAMES_PER_BUFFER, 
																dtype=gc.audio.NDARRAY_DTYPE).nbytes,
													name="audio_stream")

    process_info_list = [
        ProcessInfo(audio_stream_process, [audio_stream_shm.name,
                                           vad_stream_read_flag,
                                           audio_stream_readable_flag]),
        ProcessInfo(voice_detection_process, [gazing_flag,
                                              audio_stream_shm.name,
                                              vad_stream_read_flag,
                                              audio_stream_readable_flag]),
        ProcessInfo(gaze_detection_process, [gazing_flag]),
        # ProcessInfo(transcription_process, []),
        # ProcessInfo(get_response_process, []),
        # ProcessInfo(speech_synthesis_process, ["1"])
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
        process_list.append(process)
        LogE.d(PROCESS_NAME, f"{process.name} started")


    process = Process(target=manage_process_loading_process,
                      args=(ProcessInfo.flag_pkg_dict,))
    process_list.append(process)
    process.start()

    process = Process(target=manage_state_process,
                      args=(ProcessInfo.flag_pkg_dict,))
    process_list.append(process)
    process.start()
    
    while True:
        try:
            time.sleep(1)

        except KeyboardInterrupt:
            # 사용자가 Ctrl+C를 눌렀을 때 우아하게 종료
            print("\n[Main] 종료 신호 감지! 정리 중...")

            # 실행 중인 모든 프로세스 종료
            for p in process_list:
                if p.is_alive():
                    p.terminate() # 혹은 p.kill()
                    p.join()      # 확실히 죽었는지 확인
                    
            print("[Main] 모든 프로세스 종료 완료.")
            sys.exit(0)