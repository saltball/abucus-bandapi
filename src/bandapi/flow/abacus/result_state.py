# -*- coding: utf-8 -*-
# ====================================== #
# @Author  : Yanbo Han
# @Email   : yanbohan98@gmail.com
# @File    : result_state.py
# ALL RIGHTS ARE RESERVED UNLESS STATED.
# ====================================== #

from bandapi.flow.abacus.calculation_state import AbacusBandState
from typing import List
from bandapi.dispatcher.dpdispatcher import Task
import glob,shutil

class AbacusBandDataState(AbacusBandState):
    _state = "band-data"
    def __init__(self, task_content, flow_work_root=".", **kwargs):
        super(AbacusBandDataState, self).__init__(task_content=task_content,flow_work_root=flow_work_root,**kwargs)
        self._need_submission=False

    def flow_begin_test(self):
        for subdir, atoms in self.task_content.items():
            atoms: ase.Atoms

            logfile = glob.glob((self.flow_work_root/"nscf-band"/subdir/"OUT.ABACUS"/"running_nscf*").as_posix())
            if len(logfile)==0:
                raise FileNotFoundError
            (self.flow_work_root / self._state / subdir / "OUT.ABACUS").mkdir(parents=True,exist_ok=True)
            for item in logfile:
                shutil.copy(item,self.flow_work_root/self._state/subdir/"OUT.ABACUS/")

            BANDfile = glob.glob((self.flow_work_root / "nscf-band" / subdir / "OUT.ABACUS" / "BANDS_*.dat").as_posix())
            (self.flow_work_root / self._state / subdir / "OUT.ABACUS").mkdir(parents=True, exist_ok=True)
            for item in BANDfile:
                    shutil.copy(item, self.flow_work_root / self._state / subdir / "OUT.ABACUS/")

    def bakeup(self,task_content):
        for subdir, atoms in task_content.items():
            STRUfile = glob.glob((self.flow_work_root / "nscf-band" / subdir /"STRU").as_posix())
            for item in STRUfile:
                shutil.copy(item, self.flow_work_root / self._state / subdir)
        for subdir, atoms in task_content.items():
            INPUTfile = glob.glob((self.flow_work_root / "nscf-band" / subdir /"INPUT").as_posix())
            for item in INPUTfile:
                shutil.copy(item, self.flow_work_root / self._state / subdir)
        for subdir, atoms in task_content.items():
            KPTfile = glob.glob((self.flow_work_root / "nscf-band" / subdir /"KPT").as_posix())
            for item in KPTfile:
                shutil.copy(item, self.flow_work_root / self._state / subdir)

    def prepare(self, task_content, task_settings) -> List[Task]:
        # nothing to do for task_list
        return None

    def run_end(self, next_state):
        if next_state:
            raise RuntimeError(f"I don't not how to run {next_state} after banddata flow. Maybe you need define yours.")
        else:
            return False





