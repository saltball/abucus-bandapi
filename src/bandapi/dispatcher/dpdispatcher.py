# -*- coding: utf-8 -*-
# ====================================== #
# @Author  : Yanbo Han
# @Email   : yanbohan98@gmail.com
# @File    : dpdispatcher.py
# ALL RIGHTS ARE RESERVED UNLESS STATED.
# ====================================== #

try:
    from dpdispatcher import Machine, Resources, Task, Submission, dlog
    import time
except ImportError:
    raise ImportError("Please install dpdispatcher by `pip install dpdispatcher`")

class Submission(Submission):
    def run_submission(self, *, exit_on_submit=False, clean=True, period=40):
        """main method to execute the submission.
        First, check whether old Submission exists on the remote machine, and try to recover from it.
        Second, upload the local files to the remote machine where the tasks to be executed.
        Third, run the submission defined previously.
        Forth, wait until the tasks in the submission finished and download the result file to local directory.
        if exit_on_submit is True, submission will exit.
        """
        if not self.belonging_jobs:
            self.generate_jobs()
        self.try_recover_from_json()
        if self.check_all_finished():
            dlog.info('info:check_all_finished: True')
        else:
            dlog.info('info:check_all_finished: False')
            self.upload_jobs()
            self.handle_unexpected_submission_state()
            self.submission_to_json()
        time.sleep(1)
        while not self.check_all_finished():
            if exit_on_submit is True:
                dlog.info(f"submission succeeded: {self.submission_hash}")
                dlog.info(f"at {self.machine.context.remote_root}")
                return self.serialize()
            try:
                time.sleep(period)
            except (Exception, KeyboardInterrupt, SystemExit) as e:
                self.submission_to_json()
                dlog.exception(e)
                dlog.info(f"submission exit: {self.submission_hash}")
                dlog.info(f"at {self.machine.context.remote_root}")
                dlog.debug(self.serialize())
                raise e
            else:
                self.handle_unexpected_submission_state()
            finally:
                pass
        self.handle_unexpected_submission_state()
        self.submission_to_json()
        self.download_jobs()
        if clean:
            self.clean_jobs()
        return self.serialize()
