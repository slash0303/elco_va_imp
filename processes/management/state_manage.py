from enum import Enum

from custom_lib.flag_pkg import FlagPkg

class ProgramState(Enum):
    vad = 0
    stt = 1
    llm = 2
    tts = 3

    def next(self):
        # 1. 전체 멤버 리스트를 가져옴
        members = list(self.__class__)
        # 2. 현재 멤버의 인덱스를 찾음
        index = members.index(self)
        # 3. 다음 인덱스 계산 (모듈러 연산 % 으로 마지막 -> 처음으로 순환)
        next_index = (index + 1) % len(members)
        # 4. 해당 멤버 반환
        return members[next_index]
    
def manage_state_process(flag_pkg_dict: dict[str, FlagPkg]):
    print("mananger on")
    program_state = ProgramState(0)
    while not list(flag_pkg_dict.values())[0].sys_ready.is_set():
        pass
    
    while True:
        if program_state == ProgramState.vad:
            target_process_name = "voice_detection_process"
        elif program_state == ProgramState.stt:
            target_process_name = "transcription_process"
        elif program_state == ProgramState.llm:
            target_process_name = "get_response_process"
        elif program_state == ProgramState.tts:
            target_process_name = "speech_synthesis_process"

        target_flag_pkg = flag_pkg_dict[target_process_name]

        if not target_flag_pkg.enable.is_set():
            target_flag_pkg.clear_all()
            target_flag_pkg.enable.set()

        elif target_flag_pkg.complete.is_set():
            target_flag_pkg.enable.clear()
            program_state = program_state.next()

        elif target_flag_pkg.error.is_set():
            # 예외처리
            pass

        print(program_state.name, end="\r")