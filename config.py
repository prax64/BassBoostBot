from enum import Enum

__token = "1461016046:AAGAhwRU_Krf4miXlCuS0Rtopu8NAgFvsfQ"
db_file = "database.vdb"

__BOOST_MODE = 0
__SPEED_MODE = 1


class States(Enum):

    S_START = "0"  # Начало нового диалога
    S_ENTER_BOOST_MODE = "1"
    S_SEND_SPEED_MODE = "2"
    S_TRACK_PROCESSING_MODE = "3"
