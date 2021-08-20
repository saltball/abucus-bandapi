# -*- coding: utf-8 -*-
# ====================================== #
# @Author  : Yanbo Han
# @Email   : yanbohan98@gmail.com
# @File    : utils.py
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
from bandapi.io.abacus.potential import AbacusPotential
from bandapi.io.abacus.stru import write_abacus_stru


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
        # 'numerical_orbital_file': numerical_orbital_file, # TODO
        'pos_list': pos_list,
        'pseudo_file_list': pseudo_file_list
    }
    return stru_para_dict


def write_stur(atoms, task_root, potential_name):
    stru_para_dict = prase_atoms2strudict(atoms, potential_name)
    task_root: pathlib.Path
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

