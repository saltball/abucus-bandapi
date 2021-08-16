# -*- coding: utf-8 -*-
# ====================================== #
# @Author  : Yanbo Han
# @Email   : yanbohan98@gmail.com
# @File    : result_state.py
# ALL RIGHTS ARE RESERVED UNLESS STATED.
# ====================================== #

import glob
import shutil
from typing import List

from bandapi.dispatcher.dpdispatcher import Task
from bandapi.flow.abacus.calculation_state import AbacusBandState
from bandapi.io.abacus.out import read_fermi_energy_from_log, read_band_in_log, BandStructure, BandPath


class AbacusBandDataState(AbacusBandState):
    _state = "band-data"

    def __init__(self, task_content, flow_work_root=".", **kwargs):
        super(AbacusBandDataState, self).__init__(task_content=task_content, flow_work_root=flow_work_root, **kwargs)
        self._need_submission = False

    def flow_begin_test(self):
        for subdir, atoms in self.task_content.items():
            atoms: ase.Atoms

            nscflogfile = glob.glob((self.flow_work_root / "nscf-band" / subdir / "OUT.ABACUS" / "running_nscf*").as_posix())
            if len(nscflogfile) == 0:
                raise FileNotFoundError
            (self.flow_work_root / self._state / subdir / "OUT.ABACUS").mkdir(parents=True, exist_ok=True)
            for item in nscflogfile:
                shutil.copy(item, self.flow_work_root / self._state / subdir / "OUT.ABACUS/")

            BANDfile = glob.glob((self.flow_work_root / "nscf-band" / subdir / "OUT.ABACUS" / "BANDS_*.dat").as_posix())
            (self.flow_work_root / self._state / subdir / "OUT.ABACUS").mkdir(parents=True, exist_ok=True)
            for item in BANDfile:
                shutil.copy(item, self.flow_work_root / self._state / subdir / "OUT.ABACUS/")
            scflogfile = glob.glob((self.flow_work_root / "scf-charge" / subdir / "OUT.ABACUS" / "running_scf*").as_posix())
            for item in scflogfile:
                shutil.copy(item, self.flow_work_root / self._state / subdir / "OUT.ABACUS/")

            assert len(nscflogfile) == 1
            assert len(scflogfile) == 1

            kpathArray, bandArray = read_band_in_log(log_file=nscflogfile[0], atoms=atoms, outputfile=self.flow_work_root / self._state / subdir / "BAND")
            bandpath = BandPath(cell=atoms.cell, kpts=kpathArray, path=atoms.cell.bandpath().path, special_points=atoms.cell.bandpath().special_points)
            ferimiValues = read_fermi_energy_from_log(scflogfile[0])[-1]
            bs = BandStructure(bandpath, energies=bandArray - ferimiValues, reference=0)
            bs.plot(emin=-10, emax=10, filename=self.flow_work_root / self._state / subdir / f'{subdir}.png')

    def bakeup(self, task_content):
        for subdir, atoms in task_content.items():
            STRUfile = glob.glob((self.flow_work_root / "nscf-band" / subdir / "STRU").as_posix())
            for item in STRUfile:
                shutil.copy(item, self.flow_work_root / self._state / subdir)
        for subdir, atoms in task_content.items():
            INPUTfile = glob.glob((self.flow_work_root / "nscf-band" / subdir / "INPUT").as_posix())
            for item in INPUTfile:
                shutil.copy(item, self.flow_work_root / self._state / subdir)
        for subdir, atoms in task_content.items():
            KPTfile = glob.glob((self.flow_work_root / "nscf-band" / subdir / "KPT").as_posix())
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
