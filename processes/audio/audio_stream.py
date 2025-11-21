import pyaudio

import custom_lib.global_constants as gc
from custom_lib.flag_pkg import FlagPkg

def audio_stream_process(flag_pkg: FlagPkg):
    try:
        pa = pyaudio.PyAudio()
        
        stream = pa.open(rate=gc.audio.SAMPLING_RATE,
                        frames_per_buffer=gc.audio.FRAMES_PER_BUFFER,
                        format=gc.audio.FORMAT,
                        channels=gc.audio.CHANNELS,
                        output=True)
    except Exception as e:    
        flag_pkg.error.set()
        raise e
    
    flag_pkg.loading.clear()
    flag_pkg.loaded.set()

    while True:
        stream.read()