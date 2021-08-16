# -*- coding: utf-8 -*-
# ====================================== #
# @Author  : Yanbo Han
# @Email   : yanbohan98@gmail.com
# @File    : __init__.py.py
# ALL RIGHTS ARE RESERVED UNLESS STATED.
# ====================================== #
import abc

import dpdispatcher
from bandapi.flow.state import FlowStateControl

Default_Machine = {
    "batch_type": "Shell",
    "context_type": "LocalContext",
    # "local_root": "/",
    # "remote_root": "",
}

Default_Resource = {
    "number_node": 1,
    "cpu_per_node": 4,
    "gpu_per_node": 0,
    "queue_name": "",
    "group_size": 5000  # serialize
}


class Flow():
    def __init__(
            self, **kwargs
    ):
        """
        Tasks you defined will run as following:
        - prepare
        - gather_submission (and dispatch)
        - run_end
        - (check, e.g. add new task dynamically)
        """
        if kwargs["use_dpdispatcher"]:
            from bandapi.dispatcher.dpdispatcher import Machine, Resources
            self.machine: dpdispatcher.Machine = Machine.load_from_dict(
                {**Default_Machine, **kwargs["machine"]}
            )

            kwargs.pop("machine", None)
            self.resource: dpdispatcher.Resources = Resources.load_from_dict(
                {**Default_Resource, **kwargs["resource"]}
            )
            kwargs.pop("resource", None)

        else:
            NotImplementedError

        self._flow_state_controler=None

    @property
    def flow_state_controler(self):
        if self._flow_state_controler:
            return self._flow_state_controler
        else:
            raise NotImplementedError

    @abc.abstractmethod
    def prepare(self):
        """
        Setup a task list for flow.

        :return:
        """
        self.flow_state_controler.prepare()

    @abc.abstractmethod
    def gather_submission(self):
        """
        Gather the task and make a submission.

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def run_dispatch(self):
        """
        Run the submission with dispatch.

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def run_end(self):
        """
        Do something after dispatch.

        :return:
        """
        self.flow_state_controler.run_end()

    def submit(self, always_loop=False):
        """
        Submit task, and it will run as:
        - prepare
        - gather_submission (and run_dispatch)
        - run_end
        - (check)
            - check by using `submit_loop_condition`
        - if `submit_loop_condition` return True, loop start:
            - prepare
            - gather_submission (and run_dispatch)
            - run_end
            - (check whether to break, nor judge with `submit_loop_condition`)
        - else end
        :param always_loop:
        :return:
        """
        self.prepare()
        self.gather_submission()
        self.run_dispatch()
        self.run_end()
        while self.submit_loop_condition or always_loop:
            self.prepare()
            self.gather_submission()
            self.run_dispatch()
            self.run_end()
            if self.submit_break_condition:
                break

    @property
    def submit_loop_condition(self):
        """
        Check condition after submit run one epoch.
        :return:
        """
        return self.flow_state_controler.submit_loop_condition

    @property
    def submit_break_condition(self):
        """
        Check condition after submit loop once and further.
        :return:
        """
        return self.flow_state_controler.submit_break_condition
