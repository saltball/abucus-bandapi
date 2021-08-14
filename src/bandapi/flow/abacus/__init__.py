# -*- coding: utf-8 -*-
# ====================================== #
# @Author  : Yanbo Han
# @Email   : yanbohan98@gmail.com
# @File    : __init__.py.py
# ALL RIGHTS ARE RESERVED UNLESS STATED.
# ====================================== #
import abc
import pathlib

import dpdispatcher
from bandapi.flow import Flow

__all__ = ["AbacusFlow"]


# NOTE: In Working.


class AbacusFlowCore(Flow):
    def __init__(
            self,
            machine,
            resource,
            tasks,
            dispatch_work_base=".",
            use_dpdispatcher=True,
            restart=False,
            **kwargs
    ):
        super(AbacusFlowCore, self).__init__(
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
            self._use_dpdispatcher = False

    def run(self):

        self.dispatch_work_base = self.flow_conf["dispatch_work_base"]
        if self._use_dpdispatcher:
            from bandapi.dispatcher.dpdispatcher import Submission
            self.submission: bandapi.dispatcher.dpdispatcher.Submission = Submission(
                work_base=self.dispatch_work_base,
                machine=self.machine,
                resources=self.resource,
                task_list=self.task_list,
                forward_common_files=[],
                backward_common_files=[]
            )
        else:
            raise NotImplementedError("Undefined behavior when `_use_dpdispatcher` == False.")

    def dispatch(self):
        self.submission.run_submission(period=5)

    def run_end(self):
        pass


class AbacusFlow(AbacusFlowCore):
    def __init__(
            self,
            machine,
            resource,
            task_type,
            task_content,
            task_setup={},
            dispatch_work_base=".",
            use_dpdispatcher=True,
            **kwargs
    ):
        """

        :param machine:
        :param resource:
        :param task_type:
        :param task_content:
        :param task_setup: Some settings for task, for now, one can use following:
            `potential_name` (default: "SG15")
            `dr2` (default:`1e-07`, for all tasks.)
            `kpointrange` (default:`5`, for k-point density of relax task.)
            `abacus_path` (no default, absolute path to abacus of your server.)
            `ecutwfc` (ecutwfc, default: 50)
            `kpathrange` (default:20)

            and switch for: relax, scf, band
        :param dispatch_work_base:
        :param use_dpdispatcher:
        """
        self.task_setup = task_setup
        self.local_root = pathlib.Path(machine["local_root"]).absolute()
        self.task_type = task_type
        self.task_content = task_content
        super(AbacusFlow, self).__init__(
            machine=machine,
            resource=resource,
            tasks=None,
            use_dpdispatcher=use_dpdispatcher,
            **kwargs
        )

    def prepare(self):
        if self.task_type is not None:
            self.task_list = self.task_generate(self.task_type, self.task_content)
        else:
            raise NotImplementedError(f"None value Task_type {self.task_type} is not implemented.")

    @abc.abstractmethod
    def task_generate(self, task_type, task_content):
        """

        :param task_type:
        :param task_content:
        :return: Instance like Task() in `dpdispatcher`.
        """
        raise NotImplementedError

    def run_end(self):
        self.task_list = None
        if self.flow_conf["task_status"] == "relax" and self.task_setup["scf"]:
            self.flow_conf["task_status"] == "scf"
            raise NotImplementedError("Undefined behavior in `run_end`.")
        elif self.flow_conf["task_status"] == "scf" and self.task_setup["band"]:
            self.flow_conf["task_status"] == "band"
            raise NotImplementedError("Undefined behavior in `run_end`.")
        else:
            raise NotImplementedError("Undefined behavior in `run_end`.")
