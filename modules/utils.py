import asyncio


class Utils:

    @staticmethod
    def get_event_loop() -> asyncio.events.AbstractEventLoop:
        try:
            return asyncio.get_running_loop()
        except RuntimeError:
            return None
