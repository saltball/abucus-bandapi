# -*- coding: utf-8 -*-
# ====================================== #
# @Author  : Yanbo Han
# @Email   : yanbohan98@gmail.com
# @File    : state.py
# ALL RIGHTS ARE RESERVED UNLESS STATED.
# ====================================== #
import pathlib
from typing import List

from bandapi.dispatcher.dpdispatcher import Task


class FlowState:
    _state: str = "Unknown"
    _state_class_dict = dict()

    def __init__(self, task_content, flow_work_root=".", **kwargs):
        self._flow_work_root = pathlib.Path(flow_work_root).absolute()
        self.task_content = task_content
        self._state_settings = kwargs
        self._state_init_check()
        self._submit_loop_condition = kwargs.get("submit_loop_condition", False)
        self._submit_break_condition = kwargs.get("submit_loop_condition", False)
        self._need_submission = True  # Flow default to be submit for dispatch

    def get_state(self):
        return self._state

    def get_state_settings(self, keys, default=None):
        return self._state_settings.get(keys, default)

    @property
    def flow_work_root(self):
        """
        The root path of this **whole** flow work.

        :return: pathlib.Path
        """
        return self._flow_work_root

    def flow_begin_test(self):
        """
        Subclass(All) which need other flow results should check with this. This happens from second one of flow_list.

        """

    def _state_init_check(self):
        """
        Subclass(First class) should implement this to make sure all needed state_settings has been initialized.

        """

    def bakeup(self, task_content):
        """
        Do most I/O job to prepare task_list.

        :param: task_content:
        :return:
        """
        raise NotImplementedError

    def prepare(self, task_content, task_settings) -> List[Task]:
        """
        Set task_list of this state in the flow. Mainly do I/O check and generate List[Task,...]

        :return: List[Task,..]
        """
        raise NotImplementedError

    def run_end(self, next_state):
        """
        The state has do all necessary tasks, it's time to summary and determine what to do next.
        Make sure you give `next_state==None` a proper logic. And must return a bool to continue.

        :return: True for next_state is proper. Else stop.
        """
        raise NotImplementedError

    @property
    def submit_loop_condition(self):
        """
        If return true, the flow will loop from prepare. Maybe you haven't switch the state, be careful.

        """
        return self._submit_loop_condition

    @property
    def submit_break_condition(self):
        """
        If return true, the flow will break loop. If it not start to loop, this won't do anything.

        """
        return self._submit_break_condition

    @classmethod
    def _subclass_dict(cls):
        subclass_list = cls.__subclasses__()
        if len(subclass_list) == 0:
            cls._state_class_dict.update({cls._state: cls})
        else:
            for item in subclass_list:
                cls._state_class_dict.update({**{item._state: item}, **item._subclass_dict()})
        return cls._state_class_dict


class FlowStateControl:
    """
    Settings:
    dispatch_work_base, "."
    submission_check_period,5

    """
    _flow_state_class = FlowState

    def __init__(self, flow_list, task_content, **kwargs):
        self.flow_list = flow_list
        self._state = None
        self.flow_settings = kwargs
        self.flow_list_flag = 0
        self.task_content = task_content
        self._state_init()

    def _state_init(self,task_content=None, **kwargs):
        if not task_content:
            task_content=self.task_content
        flow = self.flow_list[self.flow_list_flag]
        self._state = self._flow_state_class._subclass_dict().get(flow)(task_content, **kwargs, **self.flow_settings)

    @property
    def state(self):
        if self._state is None:
            raise NotImplementedError(f"Initialize from {self.flow_list} failed. We only have flow state: {_flow_state_class._subclass_dict()._state}")
        else:
            return self._state

    def get_state_settings(self, key, default=None):
        if hasattr(self, key):
            return self.key
        else:
            return self._state.get_state_settings(key, default)

    def prepare(self):
        if self.flow_list_flag > -1:
            self._state.flow_begin_test()
        self._state.bakeup(self._state.task_content)
        self._state.task_list = self._state.prepare(self._state.task_content, self._state._state_settings)

    def run_end(self):
        self.flow_list_flag += 1
        try:
            if self._state.run_end(next_state=self.flow_list[self.flow_list_flag]):  # try if it's the last and run_end
                # TODO:fix the logical of loop condition
                self._submit_loop_condition = 1
                self._submit_break_condition = 0
                self._state_init(task_content=self._state.task_content,submit_loop_condition=self._submit_loop_condition, submit_break_condition=self._submit_break_condition)
            else:  # no run_end stop loop
                self._submit_loop_condition = 0
                self._submit_break_condition = 0
        except IndexError:  # no more flow, give a None, run run_end
            self._submit_loop_condition = 0
            self._submit_break_condition = 0
            self._state.run_end(next_state=None)

    @property
    def submit_loop_condition(self):
        return self._submit_loop_condition

    @property
    def submit_break_condition(self):
        return self._submit_break_condition
