# -*- coding: utf-8 -*-
# ====================================== #
# @Author  : Yanbo Han
# @Email   : yanbohan98@gmail.com
# @File    : __init__.py.py
# ALL RIGHTS ARE RESERVED UNLESS STATED.
# ====================================== #
import dpdispatcher
from bandapi.flow import Flow

__all__ = ["AbacusFlow"]

# NOTE: In Working.

class AbacusFlow(Flow):
    def __init__(
            self,
            machine,
            resource,
            tasks,
            dispatch_work_base="dispatched",
            use_dpdispatcher=True,
            restart=False,
            **kwargs
    ):
        super(AbacusFlow, self).__init__(
            machine=machine,
            resource=resource,
            tasks=tasks,
            restart=restart,
            use_dpdispatcher=use_dpdispatcher,
            **kwargs
        )
        self.flow_conf.update(dispatch_work_base=dispatch_work_base)
        try:
            self._use_dpdispatcher = use_dpdispatcher
        except KeyError:
            self._use_dpdispatcher=False


    def prepare(self):
        self.task_list = self.flow_conf["tasks"]
        self.dispatch_work_base = self.flow_conf["dispatch_work_base"]
        if self._use_dpdispatcher:
            from bandapi.dispatcher.dpdispatcher import Submission
            self.submission: dpdispatcher.Submission = Submission(
                work_base=self.dispatch_work_base,
                machine=self.machine,
                resources=self.resource,
                task_list=self.task_list,
                forward_common_files=[],
                backward_common_files=[]
            )

    def run(self):
        pass

    def dispatch(self):
        self.submission.run_submission()

    def run_end(self):
        pass
