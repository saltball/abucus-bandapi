# -*- coding: utf-8 -*-
# ====================================== #
# @Author  : Yanbo Han
# @Email   : yanbohan98@gmail.com
# @File    : __init__.py.py
# ALL RIGHTS ARE RESERVED UNLESS STATED.
# ====================================== #

default_settings = {
    "ecutwfc": 80,
    "dr2": 1.0e-7,
    "kpointscope": 5,
    "kpathscope": 20,
    "nstep": 20,
    "nbands": None,
    "kpointfix": False
}

import pathlib

import ase.symbols
from ase.atoms import Atoms
from bandapi.flow.abacus import default_settings
from bandapi.flow.abacus.utils import write_stur,write_abacus_input,write_abacus_kpt
from bandapi.flow.state import FlowState


class AbacusState(FlowState):
    _state = "Undefined"

    def __init__(self, task_content, flow_work_root, **kwargs):
        super(AbacusState, self).__init__(task_content=task_content, flow_work_root=flow_work_root, **kwargs)

    def _state_init_check(self):
        assert self.get_state_settings("potential_name") is not None
        assert self._state != "Undefined"

    def _write_stur(self, subname: pathlib.Path, atoms: Atoms, potential_name: str, flowrootdir=None):
        if flowrootdir is None:
            flowrootdir = self.flow_work_root
        write_stur(atoms, flowrootdir / self._state / subname, potential_name)

    def _write_input(self, subname: pathlib.Path, atoms: Atoms, flowrootdir=None):
        if flowrootdir is None:
            flowrootdir = self.flow_work_root
        input_args = self.get_input_args(atoms=atoms)
        write_abacus_input(task_root=(flowrootdir / self._state / subname).as_posix(),
                           input_para_dict=input_args)

    def _write_kpt(self, subname: pathlib.Path, atoms: Atoms, flowrootdir=None):
        if flowrootdir is None:
            flowrootdir = self.flow_work_root
        kpt_args = self.get_kpt_args(atoms=atoms)
        write_abacus_kpt(task_root=(flowrootdir / self._state / subname).as_posix(),
                         kpt_para_dict=kpt_args)

    def get_input_args(self, atoms):
        """
        Subclass of AbacusState must implement this.

        :param ase.Atoms atoms:
        :return:
        """
        raise NotImplementedError

    def get_kpt_args(self, atoms):
        """
        Subclass of AbacusState must implement this.

        :param ase.Atoms atoms:
        :return:
        """
        raise NotImplementedError

    def bake_upload_files(self, atoms):
        """
        Prase which files of atoms should be upload. Such as INPUT, STRU, KPT,...

        :param ase.Atoms atoms:
        :return:
        """
        raise NotImplementedError


from bandapi.flow.abacus.calculation_state import *
from bandapi.flow.abacus.result_state import *
