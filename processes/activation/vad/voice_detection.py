from multiprocessing.shared_memory import SharedMemory
from multiprocessing.synchronize import Event as EventInstance

from enum import Enum

from custom_lib.flag_pkg import FlagPkg
import custom_lib.global_constants as gc
from custom_lib.time_utilies import TimeChecker, start_timers, clear_timers
from custom_lib.eaxtension import LogE

import numpy as np
from silero_vad import load_silero_vad
import torch
import keyboard

class DetectionState(Enum):
    deactivate = 0
    speech = 1
    pause = 2
    end = 3

def voice_detection_process(flag_pkg: FlagPkg,
                            gazing_flag: EventInstance,
                            audio_stream_shm_name: str,
                            vad_stream_read_flag: EventInstance,
                            audio_stream_readable_flag: EventInstance):
    PROCESS_NAME = "voice detection"

    # Access to shared memory
    # Audio stream
    audio_data_shm = SharedMemory(name=audio_stream_shm_name)
    audio_data_ndarr = np.ndarray(gc.audio.FRAMES_PER_BUFFER, 
                                    dtype=gc.audio.NDARRAY_DTYPE, 
                                    buffer=audio_data_shm.buf)
    
    vad_model = load_silero_vad(onnx=gc.vad.USE_ONNX)

    detection_state = DetectionState(0)

    # Timers
    # Counting 'speech' duration if it's over SPEECH_LIMIT or not.
    speech_time = TimeChecker(gc.vad.SPEECH_LIMIT, print_log=True)
    # Counting Maintaining duration before switch the mode to 'pause'.
    speech_maintain_time = TimeChecker(gc.vad.MAINTAIN_LIMIT)
    # Counting 'pause' duration before terminate recording session.
    pause_time = TimeChecker(gc.vad.PAUSE_LIMIT)
    # Counting duration of whole recording session. If the duration over the RECORDING_LIMIT, the session will close.
    recording_time = TimeChecker(gc.vad.RECORDING_LIMIT)

    flag_pkg.loading.clear()

    while not flag_pkg.sys_ready.is_set():
        pass

    while True:
        if flag_pkg.enable.is_set() and gazing_flag.is_set() or keyboard.is_pressed("space"):
            vad_stream_read_flag.set()
            audio_stream_readable_flag.clear()
            # Get audio data from shared memory.
            audio_data_tensor = torch.from_numpy(audio_data_ndarr) 

            # Get activity detetction probabilty
            speech_prob = vad_model(audio_data_tensor, 
                                    gc.audio.SAMPLING_RATE).item()

            speech_detected = speech_prob >= gc.vad.ACTIVATE_THRESHOLD

            if detection_state == DetectionState.deactivate:
                LogE.p("de", 0, 10)
                if speech_detected:
                    start_timers([speech_time, 
                                  speech_maintain_time, 
                                  pause_time, 
                                  recording_time])
                    detection_state = DetectionState.speech
                else: 
                    pass

            elif detection_state == DetectionState.speech:
                LogE.p("sp", speech_maintain_time.get_time(), gc.vad.MAINTAIN_LIMIT)
                if speech_detected:
                    if speech_time.is_over() or recording_time.is_over():
                        detection_state = DetectionState.end
                    else:
                        speech_maintain_time.restart()
                else:
                    if speech_maintain_time.is_over():
                        pause_time.restart()
                        detection_state = DetectionState.pause
                    else:
                        pass

            elif detection_state == DetectionState.pause:
                LogE.p("pa", pause_time.get_time(), gc.vad.PAUSE_LIMIT)
                if speech_detected:
                    detection_state = DetectionState.speech
                else:
                    if pause_time.is_over():
                        detection_state = DetectionState.end
                    else:
                        pass
            
            elif detection_state == DetectionState.end:
                clear_timers([speech_time, speech_maintain_time, pause_time, recording_time])
                flag_pkg.complete.set()
                pass# Do something
                LogE.d("end", "end")