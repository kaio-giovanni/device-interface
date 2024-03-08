import asyncio


class Utils:

    @staticmethod
    def get_event_loop() -> asyncio.events.AbstractEventLoop:
        try:
            return asyncio.get_running_loop()
        except RuntimeError:
            return None

    @staticmethod
    def data_ready_to_be_sent(self, values) -> bool:
        return isinstance(values, list) and values.count() >= 8 and values[0] == 1