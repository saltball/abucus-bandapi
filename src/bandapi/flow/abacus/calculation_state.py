# -*- coding: utf-8 -*-
# ====================================== #
# @Author  : Yanbo Han
# @Email   : yanbohan98@gmail.com
# @File    : calculation_state.py
# ALL RIGHTS ARE RESERVED UNLESS STATED.
# ====================================== #
import glob
import pathlib
import shutil
from collections import Counter

import ase
import ase.symbols
import numpy as np
from ase.atoms import Atoms
from bandapi.dispatcher.dpdispatcher import Task
from bandapi.flow.abacus import default_settings
from bandapi.flow.abacus.utils import write_stur
from bandapi.flow.state import FlowState, FlowStateControl
from bandapi.flow.task_content import NamedAtomsContentDict
from bandapi.io.abacus.input import write_abacus_input
from bandapi.io.abacus.kpt import write_abacus_kpt
from bandapi.io.abacus.potential import AbacusPotential
from bandapi.io.abacus.out import read_stru

"""
Abacus has calculation state as following:
- scf(default)
- relax: ionic relaxations
- cell-relax: cell relaxation
- nscf: charge density file is needed.
- istate: Not Supported Now.
- ienvelope: Not Supported Now.
- md: Not Supported Now.
"""


class AbacusState(FlowState):
    _state = "Undefined"

    def __init__(self, task_content,flow_work_root, **kwargs):
        super(AbacusState, self).__init__(task_content=task_content,flow_work_root=flow_work_root, **kwargs)

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


class AbacusScfState(AbacusState):
    _state = "scf"

    def bakeup(self, task_content: NamedAtomsContentDict):
        """

        :param NamedAtomsContentDict task_content:
        :return:
        """
        for subdir, atoms in task_content.items():
            atoms: ase.Atoms
            self._write_stur(subname=subdir, atoms=atoms, potential_name=self.get_state_settings("potential_name"))
            self._write_kpt(subname=subdir, atoms=atoms)
            self._write_input(subname=subdir, atoms=atoms)

    def prepare(self, task_content: NamedAtomsContentDict, task_settings):
        task_list = []
        for idx, item in enumerate(task_content.keys()):
            for idx, item in enumerate(task_content):
                task_list.append(
                    Task(command=task_settings["remote_command"],
                         task_work_path=f"{self._state}/{item}/",
                         forward_files=[*self.bake_upload_files(task_content[item])],
                         backward_files=["OUT.ABACUS"]
                         )
                )
        return task_list

    def run_end(self, next_state: str):
        """
        Define if the next_state is able to run, and do necessary work.

        :param next_state:
        :return:
        """
        if next_state is None:
            pass
        elif next_state == "nscf-band":
            raise ValueError("Please use `AbacusScfStateWithCharge` for band-structure scf.")
        else:
            pass

    def get_input_args(self, atoms):
        """
        Implemented input_args for `scf` state.

        :param ase.Atoms atoms:
        :return:
        """
        atoms_counter = Counter(atoms.get_atomic_numbers())
        atom_type_list = list(ase.symbols.chemical_symbols[item] for item in list(atoms_counter.keys()))
        return {
            "pseudo_dir": "./",
            "calculation": "scf",
            "ntype": len(atom_type_list),
            "basis_type": "pw",
            "symmetry": 0,
            "ecutwfc": self.get_state_settings("ecutwfc", default_settings["ecutwfc"]),
            "dr2": self.get_state_settings("dr2", default_settings["dr2"]),
        }

    def get_kpt_args(self, atoms):
        """
        Implemented kpt_args for `scf` state.

        :param ase.Atoms atoms:
        :return:
        """
        scope = self.get_state_settings("kpointscope", default_settings["kpointscope"])
        odd_flag = scope % 2
        abc = atoms.cell.lengths()
        result = np.around(1 / abc / min(1 / abc) * scope)
        mask = result % 2 != odd_flag
        shift = np.zeros_like(result)
        content = np.concatenate([result + mask, shift], axis=-1)
        return {
            "number_of_kpt": 0,
            "mode": "Gamma",
            "content": content
        }

    def bake_upload_files(self, atoms):
        """
        Prase which files of atoms should be upload. Such as INPUT, STRU, KPT,...

        :param ase.Atoms atoms:
        :return:
        """
        pseudo_file_list = []
        atoms_counter = Counter(atoms.get_atomic_numbers())
        atom_type_list = list(ase.symbols.chemical_symbols[item] for item in list(atoms_counter.keys()))
        for num in atom_type_list:
            potfile: pathlib.Path = AbacusPotential(pot_name=self.get_state_settings("potential_name"))[num]
            pseudo_file_list.append(potfile.name)
        return ["INPUT", "STRU", "KPT", *pseudo_file_list]


class AbacusRelaxState(AbacusScfState, AbacusState):
    _state = "relax"

    def get_input_args(self, atoms):
        """
        Implemented input_args for `scf` state.

        :param ase.Atoms atoms:
        :return:
        """
        atoms_counter = Counter(atoms.get_atomic_numbers())
        atom_type_list = list(ase.symbols.chemical_symbols[item] for item in list(atoms_counter.keys()))
        return {
            "pseudo_dir": "./",
            "calculation": "relax",
            "ntype": len(atom_type_list),
            "basis_type": "pw",
            "symmetry": 0,
            "ecutwfc": self.get_state_settings("ecutwfc", default_settings["ecutwfc"]),
            "dr2": self.get_state_settings("dr2", default_settings["dr2"]),
        }

    def run_end(self, next_state: str):
        """
        Define if the next_state is able to run, and do necessary work.

        :param next_state:
        :return:
        """
        if next_state is None:
            pass
        elif next_state is not None:
            self._submit_loop_condition=1
            for subdir, _ in self.task_content.items():
                self.task_content[subdir]=read_stru(self.flow_work_root/self._state/subdir/"OUT.ABACUS"/"STRU_ION_D")
            return True
        else:
            raise NotImplementedError


class AbacusCellRelaxState(AbacusScfState, AbacusState):
    _state = "cell-relax"

    def get_input_args(self, atoms):
        """
        Implemented input_args for `scf` state.

        :param ase.Atoms atoms:
        :return:
        """
        atoms_counter = Counter(atoms.get_atomic_numbers())
        atom_type_list = list(ase.symbols.chemical_symbols[item] for item in list(atoms_counter.keys()))
        return {
            "pseudo_dir": "./",
            "calculation": "cell-relax",
            "ntype": len(atom_type_list),
            "basis_type": "pw",
            "symmetry": 0,
            "ecutwfc": self.get_state_settings("ecutwfc", default_settings["ecutwfc"]),
            "dr2": self.get_state_settings("dr2", default_settings["dr2"]),
            "nstep":self.get_state_settings("nstep", default_settings["nstep"]),
        }

    def run_end(self, next_state: str):
        """
        Define if the next_state is able to run, and do necessary work.

        :param next_state:
        :return:
        """
        if next_state is None:
            pass
        elif next_state == "scf"or"relax"or"scf-charge":
            self._submit_loop_condition = 1
            for subdir, _ in self.task_content.items():
                self.task_content[subdir]=read_stru(self.flow_work_root/self._state/subdir/"OUT.ABACUS"/"STRU_ION_D")
            return True
        else:
            raise NotImplementedError


class AbacusScfStateWithCharge(AbacusScfState, AbacusState):
    _state = "scf-charge"

    def get_input_args(self, atoms):
        """
        Implemented input_args for `scf` state.

        :param ase.Atoms atoms:
        :return:
        """
        atoms_counter = Counter(atoms.get_atomic_numbers())
        atom_type_list = list(ase.symbols.chemical_symbols[item] for item in list(atoms_counter.keys()))
        return {
            "pseudo_dir": "./",
            "calculation": "scf",
            "ntype": len(atom_type_list),
            "basis_type": "pw",
            "symmetry": 0,
            "ecutwfc": self.get_state_settings("ecutwfc", default_settings["ecutwfc"]),
            "dr2": self.get_state_settings("dr2", default_settings["dr2"]),
            "out_charge": 1
        }

    def run_end(self, next_state: str):
        """
        Define if the next_state is able to run, and do necessary work.

        :param next_state:
        :return:
        """
        if next_state is None:
            pass
        elif next_state == "nscf-band":
            self._submit_loop_condition = 1
            for subdir, _ in self.task_content.items():
                self.task_content[subdir]=read_stru(self.flow_work_root/self._state/subdir/"STRU")
            return True
        else:
            raise NotImplementedError


class AbacusBandState(AbacusState):
    _state = "nscf-band"

    def flow_begin_test(self):
        for subdir, atoms in self.task_content.items():
            atoms: ase.Atoms
            CHGfile = glob.glob((self.flow_work_root/"scf-charge"/subdir/"OUT.ABACUS"/"SPIN*_CHG").as_posix())
            (self.flow_work_root / self._state / subdir / "OUT.ABACUS").mkdir(parents=True,exist_ok=True)
            for item in CHGfile:
                shutil.copy(item,self.flow_work_root/self._state/subdir/"OUT.ABACUS/")

    def bakeup(self, task_content: NamedAtomsContentDict):
        """

        :param NamedAtomsContentDict task_content:
        :return:
        """
        for subdir, atoms in task_content.items():
            self._write_stur(subname=subdir, atoms=atoms, potential_name=self.get_state_settings("potential_name"))
            self._write_kpt(subname=subdir, atoms=atoms)
            self._write_input(subname=subdir, atoms=atoms)

    def prepare(self, task_content: NamedAtomsContentDict, task_settings):
        task_list = []
        for idx, item in enumerate(task_content.keys()):
            for idx, item in enumerate(task_content):
                task_list.append(
                    Task(command=task_settings["remote_command"],
                         task_work_path=f"{self._state}/{item}/",
                         forward_files=[*self.bake_upload_files(task_content[item])],
                         backward_files=["OUT.ABACUS"]
                         )
                )
        return task_list

    def run_end(self, next_state: str):
        """
        Define if the next_state is able to run, and do necessary work.

        :param next_state:
        :return:
        """
        if next_state is None:
            return False
        elif next_state=="band-data":
            return True
        else:
            return NotImplementedError

    def get_input_args(self, atoms):
        """
        Implemented input_args for `scf` state.

        :param ase.Atoms atoms:
        :return:
        """
        atoms_counter = Counter(atoms.get_atomic_numbers())
        atom_type_list = list(ase.symbols.chemical_symbols[item] for item in list(atoms_counter.keys()))
        return {
            "pseudo_dir": "./",
            "calculation": "nscf",
            "ntype": len(atom_type_list),
            "basis_type": "pw",
            "symmetry": 0,
            "ecutwfc": self.get_state_settings("ecutwfc", default_settings["ecutwfc"]),
            "dr2": self.get_state_settings("dr2", default_settings["dr2"]),
            "out_band": 1,
            "start_charge": "file"
        }

    def get_kpt_args(self, atoms):
        """
        Implemented kpt_args for `scf` state.

        :param ase.Atoms atoms:
        :return:
        """
        scope = self.get_state_settings("kpathscope", default_settings["kpathscope"])
        sp = atoms.cell.bandpath().special_points
        path = atoms.cell.bandpath().path.split(",")
        path_lines = []
        num_lines = []
        for item in path:
            for point in item:
                path_lines.append(sp[point])
                num_lines.append(scope)

            num_lines[-1] = 1
        path_lines = np.array(path_lines)
        num_lines = np.array(num_lines)
        kpathlines = np.concatenate([path_lines, num_lines[:, None]], axis=-1)
        return {
            "number_of_kpt": kpathlines.shape[0],
            "mode": "Line",
            "content": kpathlines
        }

    def bake_upload_files(self, atoms):
        """
        Prase which files of atoms should be upload. Such as INPUT, STRU, KPT,...

        :param ase.Atoms atoms:
        :return:
        """
        pseudo_file_list = []
        atoms_counter = Counter(atoms.get_atomic_numbers())
        atom_type_list = list(ase.symbols.chemical_symbols[item] for item in list(atoms_counter.keys()))
        for num in atom_type_list:
            potfile: pathlib.Path = AbacusPotential(pot_name=self.get_state_settings("potential_name"))[num]
            pseudo_file_list.append(potfile.name)
        return ["INPUT", "STRU", "KPT", *pseudo_file_list, "OUT.ABACUS/"]


class AbacusStateControl(FlowStateControl):
    _flow_state_class = AbacusState

    def __init__(self, flow_list, task_content, **kwargs):
        super(AbacusStateControl, self).__init__(flow_list=flow_list, task_content=task_content, **kwargs)
