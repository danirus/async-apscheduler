# async-apscheduler

Python async example of using an APScheduler to copy files locally. The same
concept can be used to copy files to/from AWS S3 buckets and such.

It uses the default Python event loop.

The APScheduler package offers the `AsyncIOScheduler` that runs jobs in the active event loop. The example code here schedules a single job that runs every 5 seconds.

The scheduled job checks whether there are new files in the input directory,
`data/inbox`. If there are new files the job will put them in a asyncio Queue
and will schedule 3 asyncio tasks to copy them to another directory and
delete them from the input directory.

The copy and delete file operations are done in an async executor, as the
function that copies and deletes files use sync code.

This example code must run in a single process (as it is), as otherwise there would be more than one process looking for files in the input directory, which would lead to a race condition. However the file processing uses the pseudo-
parallelism offered by asyncio, which gives fast copy ratios.

## See it in action

Create a virtualenv, enable it and `pip install -r requirements.txt`.

Create the fake data with `create_fake_data`. Run it with `-h` to read what it does:

    $ python create_fake_data 0

Launch the service locally with `python run_service.py`:

    $ python run_service.py

You will see a log like the following in stdout:

    INFO 2022-04-04 07:57:57,670 main Starting scheduler service.
    INFO 2022-04-04 07:58:02,716 main Cheching inbox dir for incoming files.
    INFO 2022-04-04 07:58:04,719 main Queueing file_00_0.csv.
    INFO 2022-04-04 07:58:06,720 main Queueing file_00_1.csv.
    Execution of job "SchedulerService.check_inbox_dir (trigger: interval[0:00:05], next run at: 2022-04-04 07:58:07 CEST)" skipped: maximum number of running insta
    nces reached (1)
    INFO 2022-04-04 07:58:08,722 main Queueing file_00_3.csv.
    INFO 2022-04-04 07:58:10,724 main Queueing file_00_2.csv.
    Execution of job "SchedulerService.check_inbox_dir (trigger: interval[0:00:05], next run at: 2022-04-04 07:58:12 CEST)" skipped: maximum number of running insta
    nces reached (1)
    INFO 2022-04-04 07:58:12,725 main Queueing file_00_6.csv.
    INFO 2022-04-04 07:58:14,727 main Queueing file_00_7.csv.
    INFO 2022-04-04 07:58:16,728 main Queueing file_00_5.csv.
    Execution of job "SchedulerService.check_inbox_dir (trigger: interval[0:00:05], next run at: 2022-04-04 07:58:17 CEST)" skipped: maximum number of running insta
    nces reached (1)
    INFO 2022-04-04 07:58:18,730 main Queueing file_00_4.csv.
    INFO 2022-04-04 07:58:20,731 main Queueing file_00_8.csv.
    INFO 2022-04-04 07:58:20,732 main I checked all the files in the inbox directory.
    INFO 2022-04-04 07:58:20,732 main I'm going to process file_00_0.csv...
    INFO 2022-04-04 07:58:20,736 main I'm going to process file_00_1.csv...
    INFO 2022-04-04 07:58:20,737 main I'm going to process file_00_3.csv...
    INFO 2022-04-04 07:58:20,745 main File file_00_3.csv has been processed in 2 seconds.
    INFO 2022-04-04 07:58:20,745 main I'm going to process file_00_2.csv...
    INFO 2022-04-04 07:58:20,745 main File file_00_0.csv has been processed in 2 seconds.
    INFO 2022-04-04 07:58:20,745 main I'm going to process file_00_6.csv...
    INFO 2022-04-04 07:58:20,746 main File file_00_1.csv has been processed in 2 seconds.
    INFO 2022-04-04 07:58:20,746 main I'm going to process file_00_7.csv...
    INFO 2022-04-04 07:58:20,753 main File file_00_6.csv has been processed in 2 seconds.
    INFO 2022-04-04 07:58:20,753 main I'm going to process file_00_5.csv...
    INFO 2022-04-04 07:58:20,753 main File file_00_2.csv has been processed in 2 seconds.
    INFO 2022-04-04 07:58:20,754 main I'm going to process file_00_4.csv...
    INFO 2022-04-04 07:58:20,754 main File file_00_7.csv has been processed in 2 seconds.
    INFO 2022-04-04 07:58:20,754 main I'm going to process file_00_8.csv...
    INFO 2022-04-04 07:58:20,760 main File file_00_5.csv has been processed in 2 seconds.
    INFO 2022-04-04 07:58:20,760 main File file_00_4.csv has been processed in 2 seconds.
    INFO 2022-04-04 07:58:20,761 main File file_00_8.csv has been processed in 2 seconds.
    INFO 2022-04-04 07:58:22,717 main Cheching inbox dir for incoming files.
    INFO 2022-04-04 07:58:22,718 main I checked all the files in the inbox directory.
    INFO 2022-04-04 07:58:27,716 main Cheching inbox dir for incoming files.
    INFO 2022-04-04 07:58:27,717 main I checked all the files in the inbox directory.
    INFO 2022-04-04 07:58:32,716 main Cheching inbox dir for incoming files.
    INFO 2022-04-04 07:58:32,718 main I checked all the files in the inbox directory.
    ^CGot signal: Signals.SIGINT, shutting down.

The `asyncio.sleep(2)` in the scheduled job makes the APScheduler hold on the
next interval, as the previous job didn't finish yet. And we want only 1
instance of this job: `max_instances=1`.