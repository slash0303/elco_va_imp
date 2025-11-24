from multiprocessing.shared_memory import SharedMemory
from multiprocessing.synchronize import Event as EventInstance

import pyaudio
import numpy as np

import custom_lib.global_constants as gc
from custom_lib.flag_pkg import FlagPkg

def audio_stream_process(flag_pkg: FlagPkg,
                         audio_stream_shm_name: str,
                         stream_read_flag_list: list[EventInstance],
                         audio_stream_readable_flag: EventInstance):
    try:
        pa = pyaudio.PyAudio()
        
        stream = pa.open(rate=gc.audio.SAMPLING_RATE,
                        frames_per_buffer=gc.audio.FRAMES_PER_BUFFER,
                        format=gc.audio.FORMAT,
                        channels=gc.audio.CHANNELS,
                        input=True)
        
        audio_stream_mem = SharedMemory(name=audio_stream_shm_name)
        audio_stream_buf = np.ndarray(gc.audio.FRAMES_PER_BUFFER,
                                      dtype=gc.audio.NDARRAY_DTYPE,
                                      buffer=audio_stream_mem.buf)

    except Exception as e:    
        flag_pkg.error.set()
        raise e
    
    flag_pkg.loading.clear()

    while True:
        all_read = True
        for stream_read_flag in stream_read_flag_list:
            all_read = all_read and stream_read_flag.is_set()
        if all_read:
            audio_data = np.frombuffer(stream.read(gc.audio.FRAMES_PER_BUFFER),
                                        dtype=np.int16)
            np.copyto(audio_stream_buf, audio_data)
            audio_stream_readable_flag.set()
            for stream_read_flag in stream_read_flag_list:
                stream_read_flag.clear()
        else:
            pass