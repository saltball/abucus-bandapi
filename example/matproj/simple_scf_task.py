# -*- coding: utf-8 -*-
# ====================================== #
# @Author  : Yanbo Han
# @Email   : yanbohan98@gmail.com
# @File    : simple_scf_task.py
# ALL RIGHTS ARE RESERVED UNLESS STATED.
# ====================================== #
import pathlib
import shutil
from collections import Counter

import ase.data
import ase.lattice
import ase.symbols
import numpy as np
from bandapi.dispatcher.dpdispatcher import Task
from bandapi.io.abacus.input import write_abacus_input
from bandapi.io.abacus.kpt import write_abacus_kpt
from bandapi.io.abacus.potential import AbacusPotential
from bandapi.io.abacus.stru import write_abacus_stru
from bandapi.third_part.matproj import MatProjWrapper
from bandapi.flow.abacus import AbacusFlow

ABACUS_COMMAND = r"/home/ubuntu/abacus-develop/build/abacus"
CPU_NUM = 8

API_KEY = ""  # SETUP THIS

LOCAL_ROOT = pathlib.Path(r"./dispatcher")

machine = {
    "batch_type": "shell",
    "context_type": "SSHContext",
    "local_root": LOCAL_ROOT.as_posix(),
    "remote_root": "/home/ubuntu/work/dispatcher", # SETUP THIS
    "remote_profile": {

        "hostname": "",  # SETUP THIS
        "username": "",  # SETUP THIS
        "password": "",  # SETUP THIS
        "port": 22,
        "timeout": 10

    }
}

resource = {
    "number_node": 1,
    "cpu_per_node": CPU_NUM,
    "group_size": 5
}

matprojw = MatProjWrapper(API_KEY=API_KEY)


# get stru
def get_mat_proj_with_id(mat_proj_id):
    result = matprojw.get_structure_by_id(mat_proj_id)
    return result


def prase_atoms2strudict(atoms: ase.atoms, potential_name="SG15"):
    atoms_counter = Counter(atoms.get_atomic_numbers())
    atom_type_list = list(ase.symbols.chemical_symbols[item] for item in list(atoms_counter.keys()))
    coordinate_type = "Cartesian"
    label_list = atom_type_list
    lattice_constant = atoms.cell.lengths().max()
    lattice_matrix = atoms.cell / lattice_constant
    magnetism_list = np.ones_like(atom_type_list)
    mass_list = list([ase.data.atomic_masses[item] for item in list(atoms_counter.keys())])
    number_of_atoms_list = list(atoms_counter.values())
    pos_list = []
    for num in atoms_counter.keys():
        pos_item = atoms.positions[atoms.get_atomic_numbers() == num] / lattice_constant
        pos_list.append(np.concatenate([pos_item, np.zeros_like(pos_item)], axis=-1))
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


def write_stur(atoms):
    stru_para_dict = prase_atoms2strudict(atoms)
    task_root: pathlib.Path = (LOCAL_ROOT / "dir1")
    if not task_root.exists():
        task_root.mkdir(parents=True)
    write_abacus_stru(task_root=task_root.as_posix(),
                      stru_para_dict=stru_para_dict)
    return stru_para_dict


def write_input(**kwargs):
    task_root: pathlib.Path = (LOCAL_ROOT / "dir1")
    write_abacus_input(task_root=task_root.as_posix(),
                       input_para_dict=kwargs)


def write_kpt(**kwargs):
    task_root: pathlib.Path = (LOCAL_ROOT / "dir1")
    write_abacus_kpt(task_root=task_root.as_posix(),
                     kpt_para_dict=kwargs)


def copy_pseudo_file_list(stru_info: dict, pot_name="SG15"):
    atom_type_list = stru_info["atom_type_list"]

    for num in atom_type_list:
        potfile: pathlib.Path = AbacusPotential(pot_name=pot_name)[num]
        shutil.copy(potfile, LOCAL_ROOT / "dir1")


if __name__ == '__main__':
    atoms_list = get_mat_proj_with_id("mp-24")
    atoms = atoms_list[0]
    stru_info = write_stur(atoms)
    write_input(pseudo_dir="./",
                calculation="scf",
                ntype=1,
                nbands=16,
                basis_type="pw",
                symmetry=0,
                ecutwfc=50,
                dr2=1.0e-7,
                nstep=1,
                out_charge=1)
    write_kpt(number_of_kpt=0,
              mode="Gamma",
              content=[4, 4, 4, 0, 0, 0])

    copy_pseudo_file_list(stru_info)

    task_list = [
        Task(command=f"mpirun -np {CPU_NUM} {ABACUS_COMMAND}",
             task_work_path="dir1/",
             forward_files=["INPUT", "KPT", "STRU", *stru_info["pseudo_file_list"]],
             backward_files=["OUT.ABACUS"]
             )
    ]
    flow = AbacusFlow(machine=machine,
                      resource=resource,
                      tasks=task_list,
                      use_dpdispatcher=True,
                      dispatch_work_base="."
                      )

    flow.submit()
