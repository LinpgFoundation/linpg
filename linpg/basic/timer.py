from .display import *

# bool timer use for tick checking
class BoolTickTimer:
    def __init__(self, time_ms: int, default_status: bool = True) -> None:
        self.__time_to_wait = time_ms
        self.__current_time: int = 0
        self.__status: bool = default_status
        self.__prev_status: bool = self.__status

    def tick(self) -> None:
        self.__current_time += Display.get_delta_time()
        self.__prev_status = self.__status
        if self.__current_time > self.__time_to_wait:
            self.__current_time = 0
            self.__status = not self.__status

    def is_status_changed(self) -> bool:
        return self.__prev_status != self.__status

    def get_status(self) -> bool:
        return self.__status
