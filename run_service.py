import asyncio
import logging.config
from signal import SIGINT, SIGTERM

# In case you want to use evloop, a faster event loop
# implementation: https://uvloop.readthedocs.io/index.html
# import uvloop

from app.config import LOGGING
from app.main import main


def handler(sig):
    loop = asyncio.get_event_loop()
    loop.stop()
    print(f'Got signal: {sig!s}, shutting down.')
    loop.remove_signal_handler(SIGTERM)
    loop.add_signal_handler(SIGINT, lambda: None)


if __name__ == "__main__":
    logging.config.dictConfig(LOGGING)

    # Create the event loop. The comment line would do the same
    # but using the uvloop: https://uvloop.readthedocs.io/index.html
    loop = asyncio.new_event_loop()
    # loop = uvloop.new_event_loop()

    asyncio.set_event_loop(loop)

    for sig in (SIGTERM, SIGINT):
        loop.add_signal_handler(sig, handler, sig)

    loop.create_task(main())
    loop.run_forever()
    loop.close()
