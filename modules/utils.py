import asyncio


class Utils:

    @staticmethod
    def get_event_loop() -> asyncio.events.AbstractEventLoop:
        try:
            return asyncio.get_running_loop()
        except RuntimeError:
            return None

    @staticmethod
    def split_word(word, byte_order):
        byte1 = (word >> 8) & 0xFF
        byte0 = word & 0xFF
        if byte_order == 'BIG':
            return byte0, byte1
        else:
            return byte1, byte0

    @staticmethod
    def words_to_string(word_array, byte_order='BIG'):
        bytes_list = []
        for word in word_array:
            byte1, byte0 = Utils.split_word(word, byte_order)
            bytes_list.append(byte1)
            bytes_list.append(byte0)
        return ''.join(chr(byte) for byte in bytes_list)
