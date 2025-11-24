from custom_lib.flag_pkg import FlagPkg
from multiprocessing.shared_memory import SharedMemory
from multiprocessing.synchronize import Event as EventInstance
import custom_lib.global_constants as gc


from whisper_streaming.whisper_online import *

def transcription_process(flag_pkg: FlagPkg,
                          audio_stream_shm_name: str,
                          stt_stream_read: EventInstance):
    src_lan = "kr"
    tgt_lan = "kr"

    asr = FasterWhisperASR(src_lan, "small")
    online = OnlineASRProcessor(asr)  # create processing object with default buffer trimming option

    flag_pkg.loading.clear()

    audio_data_shm = SharedMemory(name=audio_stream_shm_name)
    audio_data_ndarr = np.ndarray(gc.audio.FRAMES_PER_BUFFER, 
                                    dtype=gc.audio.NDARRAY_DTYPE, 
                                    buffer=audio_data_shm.buf)

    while True:
        if flag_pkg.enable.is_set():
            stt_stream_read.set()
            a = audio_data_ndarr # receive new audio chunk (and e.g. wait for min_chunk_size seconds first, ...)
            online.insert_audio_chunk(a)
            o = online.process_iter()
            print(o) # do something with current partial output
        # at the end of this audio processing
        o = online.finish()
        print(o)  # do something with the last output

        online.init()