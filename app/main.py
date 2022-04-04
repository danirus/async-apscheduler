import asyncio
import logging
import os
import shutil

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app import config


logger = logging.getLogger(__name__)


# This function uses blocking to operate on files using the shutil and os
# packages. The interesting thing of the function is that in the next function
# (process_file) we run it within an executor, so that it can be used in the
# event loop of asyncio. It has more cost in terms of switching contexts due to
# the use of a Thread to run it, but it has the benefit that the copy and
# delete can be done in a non-blocking way allowing the rest of the tasks in
# the event loop to have a chance to run.
#
def copy_and_delete_file(filename: str):
    input_file_path = config.INBOX_PATH / filename
    shutil.copy(input_file_path, config.PROCESSED_PATH)
    os.remove(input_file_path)


# This is the worker function of which we create 3 tasks that run in the event
# loop. The function reads from the queue until there is no more elements.
# When it reaches the end of the queue the function await in the queue.get(),
# so in the caller (check_inbox_dir method) we collect them and cancel them.
#
# The interesting part of the function is the usage of an executor in
# loop.run_in_executor. When the first arg is None the executor uses a
# ThreadPoolExecutor. I pass the name of the sync function I want to run in the
# executor (which is coded above these lines) and the argument I pass to the
# function, which is the filename I got from the queue.
#
async def process_file(queue):
    loop = asyncio.get_event_loop()
    while True:
        filename = await queue.get()
        logger.info(f"I'm going to process {filename}...")
        await loop.run_in_executor(None, copy_and_delete_file, filename)
        queue.task_done()
        logger.info(f"File {filename} has been processed in 2 seconds.")


class SchedulerService:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.sch = AsyncIOScheduler()

    async def check_inbox_dir(self):
        logger.info("Cheching inbox dir for incoming files.")
        for filename in os.listdir(config.INBOX_PATH):
            await asyncio.sleep(2)
            logger.info(f"Queueing {filename}.")
            self.queue.put_nowait(filename)
        logger.info("I checked all the files in the inbox directory.")

        # Create 3 workers to process the queue concurrently.
        tasks = []
        for i in range(3):
            task = asyncio.create_task(process_file(self.queue))
            tasks.append(task)
        await self.queue.join()

        # Cancel our worker tasks.
        for task in tasks:
            # I have to cancel them because they stand waiting
            # for more elements in the queue with queue.get()
            task.cancel()

        # Wait until all worker tasks are cancelled.
        await asyncio.gather(*tasks, return_exceptions=True)


    def start(self):
        if not os.path.exists(config.PROCESSED_PATH):
            os.mkdir(config.PROCESSED_PATH)
        logger.info("Starting scheduler service.")
        self.sch.start()
        self.sch.add_job(self.check_inbox_dir, 'interval',
                         # Using max_instances=1 guarantees that only one job
                         # runs at the same time (in this event loop).
                         seconds=5, max_instances=1)

async def main():
    sch_srv = SchedulerService()
    sch_srv.start()
