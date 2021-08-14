# -*- coding: utf-8 -*-
# ====================================== #
# @Author  : Yanbo Han
# @Email   : yanbohan98@gmail.com
# @File    : matproj.py
# ALL RIGHTS ARE RESERVED UNLESS STATED.
# ====================================== #

import pathlib
import shutil
from collections import Counter

import ase.data
import ase.lattice
import ase.symbols
import numpy as np
from bandapi.io.abacus.input import write_abacus_input
from bandapi.io.abacus.kpt import write_abacus_kpt
from bandapi.io.abacus.out import read_stru
from bandapi.io.abacus.potential import AbacusPotential
from bandapi.io.abacus.stru import write_abacus_stru
from bandapi.third_part.matproj import MatProjWrapper
from dpdispatcher import Task

from ..abacus import AbacusFlow


def prase_atoms2strudict(atoms: ase.atoms, potential_name="SG15"):
    """

    :param atoms:
    :param potential_name:
    :return:
    """
    atoms_counter = Counter(atoms.get_atomic_numbers())
    atom_type_list = list(ase.symbols.chemical_symbols[item] for item in list(atoms_counter.keys()))
    coordinate_type = "Cartesian"
    label_list = atom_type_list
    lattice_constant = atoms.cell.lengths().max()
    lattice_matrix = atoms.cell / lattice_constant
    magnetism_list = list(0 for item in atom_type_list)
    mass_list = list([ase.data.atomic_masses[item] for item in list(atoms_counter.keys())])
    number_of_atoms_list = list(atoms_counter.values())
    pos_list = []
    for num in atoms_counter.keys():
        pos_item = atoms.positions[atoms.get_atomic_numbers() == num] / lattice_constant
        pos_list.append(np.concatenate([pos_item, np.ones_like(pos_item)], axis=-1))
    pseudo_file_list = []
    for num in atom_type_list:
        potfile: pathlib.Path = AbacusPotential(pot_name=potential_name)[num]
        pseudo_file_list.append(potfile.name)
    stru_para_dict = {
        'atom_type_list': atom_type_list,
        'coordinate_type': coordinate_type,
        'label_list': label_list,
        'lattice_constant': lattice_constant,
        'lattice_matrix': lattice_matrix,
        'magnetism_list': magnetism_list,
        'mass_list': mass_list,
        'number_of_atoms_list': number_of_atoms_list,
        # 'numerical_orbital_file': numerical_orbital_file,
        'pos_list': pos_list,
        'pseudo_file_list': pseudo_file_list
    }
    return stru_para_dict


def write_stur(atoms, local_root, idx, potential_name):
    stru_para_dict = prase_atoms2strudict(atoms, potential_name)
    task_root: pathlib.Path = (local_root / idx)
    if not task_root.exists():
        task_root.mkdir(parents=True)
    write_abacus_stru(task_root=task_root.as_posix(),
                      stru_para_dict=stru_para_dict)
    copy_pseudo_file_list(task_root=task_root, atom_type_list=stru_para_dict["atom_type_list"], pot_name=potential_name)
    return stru_para_dict


def copy_pseudo_file_list(task_root, atom_type_list, pot_name="SG15"):
    for num in atom_type_list:
        potfile: pathlib.Path = AbacusPotential(pot_name=pot_name)[num]
        shutil.copy(potfile, task_root)


def write_input(local_root, idx, **kwargs):
    task_root: pathlib.Path = (local_root / idx)
    write_abacus_input(task_root=task_root.as_posix(),
                       input_para_dict=kwargs)


def write_kpt(local_root, idx, **kwargs):
    task_root: pathlib.Path = (local_root / idx)
    write_abacus_kpt(task_root=task_root.as_posix(),
                     kpt_para_dict=kwargs)


class AbacusFlowFromMatProj(AbacusFlow):
    def __init__(self, API_KEY, **kwargs):
        """
        Setup an ABACUS workflow from data of material project.
        :param API_KEY: Your Material Project API_KEY
        :param machine: Machine dict or str(for json file), same to dpdispatcher
        :param resource: Resource dict or str(for json file), same to dpdispatcher
        :param task_type: str, now only "matprojid"
        :param task_content: Union[List], for id string of material project.
        :param task_setup: dict, default to {},
        :param dispatch_work_base: str or path-like, default to ".",
        :param use_dpdispatcher: bool, default using dpdispatcher(True).
        """
        self.matprojwrapper = MatProjWrapper(API_KEY=API_KEY)
        assert self.matprojwrapper.test_connet()
        super(AbacusFlowFromMatProj, self).__init__(**kwargs)

    def task_generate(self, task_source_type, task_content):
        if task_source_type == "matprojid":
            try:
                self.flow_conf["task_status"]
            except KeyError:
                if self.task_setup["relax"]:
                    self.flow_conf["task_status"] = "relax"
                elif self.task_setup["scf"]:
                    self.flow_conf["task_status"] = "scf"
                elif self.task_setup["band"]:
                    self.flow_conf["task_status"] = "band"
                else:
                    raise NotImplementedError("I don't know what to do when setting none of relax, scf and scf.")
            stru_info_list = self.convert(task_content)
            return self.task_prepare(task_content, stru_info_list)
        else:
            raise NotImplementedError

    def task_prepare(self, task_content, stru_info_list):
        """
        task_prepare() function will makeup task instances list for flow.(No matter how you download the file.)
        It assume your task is named as items in task_content and locate in `local_root`. (This setup with machine dict.)
        This will prepare task as following:
            if not defined `self.flow_conf["task_status"]` or you explicitly defined `relax`:
                a new flow, prepare task as relax task.
            elif `scf`,
            elif `band`,
            others will raise an error.
        :param task_content:
        :param stru_info_list: structure information to set up the tasks.
        :return:
        """
        task_list = []
        if self.flow_conf["task_status"] == "relax":
            for idx, item in enumerate(task_content):
                task_list.append(
                    Task(command=f"mpirun -np {self.resource.cpu_per_node} {self.task_setup['abacus_path']}",
                         task_work_path=f"{self.flow_conf['task_status']}/{item}/",
                         forward_files=["INPUT", "KPT", "STRU", *stru_info_list[idx]["pseudo_file_list"]],
                         backward_files=["OUT.ABACUS"]
                         )
                )
        elif self.flow_conf["task_status"] == "scf":
            for idx, item in enumerate(task_content):
                task_list.append(
                    Task(command=f"mpirun -np {self.resource.cpu_per_node} {self.task_setup['abacus_path']}",
                         task_work_path=f"{self.flow_conf['task_status']}/{item}/",
                         forward_files=["INPUT", "KPT", "STRU", *stru_info_list[idx]["pseudo_file_list"]],  # band-structure calculation need out.abacus file(s) spin_chgcar*
                         backward_files=["OUT.ABACUS"]
                         )
                )
        elif self.flow_conf["task_status"] == "band":
            for idx, item in enumerate(task_content):
                task_list.append(
                    Task(command=f"mpirun -np {self.resource.cpu_per_node} {self.task_setup['abacus_path']}",
                         task_work_path=f"{self.flow_conf['task_status']}/{item}/",
                         forward_files=["INPUT", "KPT", "STRU", *stru_info_list[idx]["pseudo_file_list"], "OUT.ABACUS/"],  # band-structure calculation need out.abacus file(s) spin_chgcar*
                         backward_files=["OUT.ABACUS"]
                         )
                )
        else:
            raise NotImplementedError
        return task_list

    def convert(self, task_content):
        """
        download() function will makeup all directories with INPUT, KPT and STRU files.
        :param task_content:
        :return:
        """
        stru_info_list = []
        if self.flow_conf["task_status"] == "relax":
            for idx, item in enumerate(task_content):
                result = self.matprojwrapper.get_structure_by_id(item)
                assert len(result) == 1, "Got not only one structure, it's undefined behavior."
                result = result[0]
                local_root = self.local_root / self.flow_conf["task_status"]

                stru_info = write_stur(result, local_root, item, potential_name=self.task_setup["potential_name"])

                input_args = self.get_relax_input_args(result, stru_info)
                write_input(local_root, item, **input_args)

                kpt_args = self.get_relax_kpt_args(result, stru_info)
                write_kpt(local_root, item, **kpt_args)
                stru_info_list.append(stru_info)
            return stru_info_list
        elif self.flow_conf["task_status"] == "scf":
            for idx, item in enumerate(task_content):
                if not self.task_setup["relax"]:  # not relax but need data. directly scf.
                    result = self.matprojwrapper.get_structure_by_id(mat_proj_id)
                    assert len(result) == 1, "Got not only one structure, it's undefined behavior."
                    result: ase.Atoms = result[0]
                else:  # after relax.
                    result: ase.Atoms = self.get_structure_from_relax_tasks(self.local_root / "relax" / item)
                local_root = self.local_root / self.flow_conf["task_status"]

                stru_info = write_stur(result, local_root, item, potential_name=self.task_setup["potential_name"])

                input_args = self.get_scf_input_args(result, stru_info)
                write_input(local_root, item, **input_args)

                kpt_args = self.get_scf_kpt_args(result, stru_info)
                write_kpt(local_root, item, **kpt_args)
                stru_info_list.append(stru_info)
            return stru_info_list
        elif self.flow_conf["task_status"] == "band":
            for idx, item in enumerate(task_content):
                if not self.task_setup["scf"]:  # not relax but need data. directly band.
                    raise RuntimeError("I don't how to run tasks without scf results.")
                else:  # after relax.
                    result = self.get_structure_from_scf_tasks(self.local_root / "scf")
                local_root = self.local_root / self.flow_conf["task_status"]

                stru_info = write_stur(result, local_root, item, potential_name=self.task_setup["potential_name"])

                input_args = self.get_band_input_args(result, stru_info)
                write_input(local_root, item, **input_args)

                kpt_args = self.get_band_kpt_args(result, stru_info)
                write_kpt(local_root, item, **kpt_args)
                stru_info_list.append(stru_info)
            return stru_info_list
        else:
            raise NotImplementedError

    def get_relax_input_args(self, atoms, stru_info):
        """

        :param atoms:
        :param stru_info: info dictionary from `write_stur`
        :return:
        """
        return {
            "pseudo_dir": "./",
            "calculation": "relax",
            "ntype": len(stru_info["atom_type_list"]),
            # "nbands": 8,
            "basis_type": "pw",
            "symmetry": 0,
            "ecutwfc": self.task_setup.get("ecutwfc", 50),
            "dr2": self.task_setup.get("dr2", 1.0e-7),
            # "nstep": 1,
            "out_charge": 1
        }

    def get_relax_kpt_args(self, atoms, stru_info):
        """

        :param atoms:
        :param stru_info: info dictionary from `write_stur`
        :return:
        """
        return {
            "number_of_kpt": 0,
            "mode": "Gamma",
            "content": self.get_relax_kpt_array(atoms.cell.lengths(), self.task_setup.get("kpointrange", 5))
        }

    def get_relax_kpt_array(self, abc, range=5):
        """
        More range, more kpoints. Change here if anyone want other methods to generate k-points.
        :param abc:
        :param range: int
        :return:
        """

        result = np.around(1 / abc / min(1 / abc) * range)
        shift = np.zeros_like(result)
        return np.concatenate([result, shift], axis=-1)

    #### For scf job

    def get_structure_from_relax_tasks(self, relax_path: pathlib.Path):
        return read_stru(relax_path / "OUT.ABACUS/STRU_ION_D")

    def get_scf_input_args(self, atoms, stru_info):
        """

        :param atoms:
        :param stru_info: info dictionary from `write_stur`
        :return:
        """
        return {
            "pseudo_dir": "./",
            "calculation": "scf",
            "ntype": len(stru_info["atom_type_list"]),
            # "nbands": 8,
            "basis_type": "pw",
            "symmetry": 0,
            "ecutwfc": self.task_setup.get("ecutwfc", 50),
            "dr2": self.task_setup.get("dr2", 1.0e-7),
            # "nstep": 1,
            "out_charge": 1
        }

    def get_scf_kpt_args(self, atoms, stru_info):
        """

        :param atoms:
        :param stru_info: info dictionary from `write_stur`
        :return:
        """
        return {
            "number_of_kpt": 0,
            "mode": "Gamma",
            "content": self.get_relax_kpt_array(atoms.cell.lengths(), self.task_setup.get("kpointrange", 5) + 2)  # FIXME: is it necessary to use more kpoints?
        }

    #### For band jobs
    def get_band_input_args(self, atoms, stru_info):
        """

        :param atoms:
        :param stru_info: info dictionary from `write_stur`
        :return:
        """
        return {
            "pseudo_dir": "./",
            "calculation": "nscf",
            "ntype": len(stru_info["atom_type_list"]),
            # "nbands": 8,
            "basis_type": "pw",
            "symmetry": 0,
            "ecutwfc": self.task_setup.get("ecutwfc", 50),
            "dr2": self.task_setup.get("dr2", 1.0e-7),
            # "nstep": 1,
            "out_band": 1,
            "start_charge": "file"
        }

    def get_band_kpt_args(self, atoms, stru_info):
        """

        :param atoms:
        :param stru_info: info dictionary from `write_stur`
        :return:
        """
        return {
            "number_of_kpt": 6,
            "mode": "Line",
            "content": self.get_relax_kpt_array(atoms, self.task_setup.get("kpointrange", 5))
        }

    def get_band_kpt_array(self, atoms, range=5):
        """
        More range, more kpoints. Change here if anyone want other methods to generate k-points.
        :param atoms:
        :param range: int
        :return:
        """
        sp = atoms.cell.bandpath().special_points
        path = atoms.cell.bandpath().path.split(",")
        path_lines = []
        num_lines = []
        for item in path:
            for point in item:
                path_lines.append(sp[point])
                num_lines.append(20)
            num_lines[-1] = 1
        path_lines = np.array(path_lines)
        num_lines = np.array(num_lines)
        kpathlines = np.concatenate([path_lines, num_lines[:, None]], axis=-1)
        return kpathlines

    def run_end(self):
        local_origin_root = self.local_root / self.flow_conf["task_status"]
        if self.flow_conf["task_status"] == "relax" and self.task_setup["scf"]:
            # local_new_root = self.local_root / self.flow_conf["task_status"]
            # pass
            self.flow_conf["task_status"] = "scf"
            self.flow_conf["task_status_type"] = "ongoing"
        elif self.flow_conf["task_status"] == "scf" and self.task_setup["band"]:
            local_new_root = self.local_root / self.flow_conf["task_status"]
            for item in self.task_content:
                shutil.copy(local_origin_root / item / "OUT.ABACUS/SPIN*_CHGCAR", local_new_root / item / "OUT.ABACUS/")
            self.flow_conf["task_status"] = "band"
            self.flow_conf["task_status_type"] = "ongoing"
        else:
            raise NotImplementedError("Undefined behavior in `run_end`.")
        self.task_list = None

    def submit_loop_condition(self):
        if self.flow_conf["task_status_type"] == "ongoing":
            return True
        else:
            return False
