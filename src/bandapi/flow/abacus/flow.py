# -*- coding: utf-8 -*-
# ====================================== #
# @Author  : Yanbo Han
# @Email   : yanbohan98@gmail.com
# @File    : flow.py
# ALL RIGHTS ARE RESERVED UNLESS STATED.
# ====================================== #
from bandapi.flow import Flow
from bandapi.flow.abacus.calculation_state import AbacusStateControl


class AbacusFlow(Flow):
    def __init__(
            self,
            machine,
            resource,
            task_flow_list,
            task_content,
            task_setup,
            use_dpdispatcher=True
    ):
        super(AbacusFlow, self).__init__(
            machine=machine,
            resource=resource,
            use_dpdispatcher=use_dpdispatcher
        )
        try:
            self._use_dpdispatcher = use_dpdispatcher
        except KeyError:
            self._use_dpdispatcher = False
        self._flow_state_controler = AbacusStateControl(
            flow_list=task_flow_list,task_content=task_content, **task_setup
        )

    def gather_submission(self):
        if self.flow_state_controler._state._need_submission:
            dispatch_work_base = self.flow_state_controler.get_state_settings("dispatch_work_base", ".")
            if self._use_dpdispatcher:
                from bandapi.dispatcher.dpdispatcher import Submission
                if self.flow_state_controler._state.task_list:
                    self.submission: bandapi.dispatcher.dpdispatcher.Submission = Submission(
                        work_base=dispatch_work_base,
                        machine=self.machine,
                        resources=self.resource,
                        task_list=self.flow_state_controler._state.task_list,
                        forward_common_files=[],
                        backward_common_files=[]
                    )
            else:
                raise NotImplementedError("Undefined behavior when `_use_dpdispatcher` == False.")
        else:
            pass

    def run_dispatch(self):
        if self.flow_state_controler._state._need_submission:
            if hasattr(self,"submission"):
                self.submission.run_submission(period=self.flow_state_controler.get_state_settings("submission_check_period", 5),clean=self.flow_state_controler.get_state_settings("clean",True))
        else:
            pass
