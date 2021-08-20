# -*- coding: utf-8 -*-
# ====================================== #
# @Author  : Yanbo Han
# @Email   : yanbohan98@gmail.com
# @File    : stru.py
# ALL RIGHTS ARE RESERVED UNLESS STATED.
# ====================================== #
import pathlib
from collections import OrderedDict

import numpy as np
from ase.units import Angstrom, Bohr

AbacusStruKeyDict = OrderedDict()
AbacusStruKeyDict.update({
    "ATOMIC_SPECIES":
        [
            "label_list",
            "mass_list",
            "pseudo_file_list",
        ],
    "NUMERICAL_ORBITAL":
        [
            "numerical_orbital_file",
        ],
    "LATTICE_CONSTANT":  # unit:Bohr, but input(in this package) is Ang
        [
            "lattice_constant",
        ],
    "LATTICE_VECTORS":
        [
            "lattice_matrix",  # 3by3 matrix
        ],
    "ATOMIC_POSITIONS":
        [
            "coordinate_type",  # Cartesian or Direct
            "atom_type_list",
            "magnetism_list",
            "number_of_atoms_list",
            "pos_list",  # posx posy posz flagx flagy flagz
        ]
})

AbacusStruBlock = {'atom_type_list': 'ATOMIC_POSITIONS',
                   'coordinate_type': 'ATOMIC_POSITIONS',
                   'label_list': 'ATOMIC_SPECIES',
                   'lattice_constant': 'LATTICE_CONSTANT',  # unit: same as ase, Ang, convert to Bohr by program.
                   'lattice_matrix': 'LATTICE_VECTORS',
                   'magnetism_list': 'ATOMIC_POSITIONS',
                   'mass_list': 'ATOMIC_SPECIES',
                   'number_of_atoms_list': 'ATOMIC_POSITIONS',
                   'numerical_orbital_file': 'NUMERICAL_ORBITAL',
                   'pos_list': 'ATOMIC_POSITIONS',
                   'pseudo_file_list': 'ATOMIC_SPECIES'}


def write_abacus_stru(
        task_root: str,
        stru_para_dict: dict
):
    all_stru_keys = stru_para_dict.keys()
    stru_blocks = set()
    for key in all_stru_keys:
        try:
            stru_blocks.add(AbacusStruBlock[key])
        except KeyError:
            raise KeyError(f"Invalid STRU Key for ABACUS: {key}")
    with open(pathlib.Path(task_root) / "STRU", "w") as f:
        # MUST IN ORDER
        if "ATOMIC_SPECIES" in stru_blocks:
            print(generate_atom_species_lines(stru_para_dict), file=f)
        if "NUMERICAL_ORBITAL" in stru_blocks:
            print(generate_numerical_orbital_lines(stru_para_dict), file=f)
        if "LATTICE_CONSTANT" in stru_blocks:
            print(generate_lattice_constant_lines(stru_para_dict), file=f)
        if "LATTICE_VECTORS" in stru_blocks:
            print(generate_lattice_vectors_lines(stru_para_dict), file=f)
        if "ATOMIC_POSITIONS" in stru_blocks:
            print(generate_atomic_positions_lines(stru_para_dict), file=f)


def generate_atom_species_lines(stru_para_dict):
    # ATOMIC_SPECIES lines
    label_list = stru_para_dict["label_list"]
    mass_list = stru_para_dict["mass_list"]
    pseudo_file_list = stru_para_dict["pseudo_file_list"]
    assert len(label_list) == len(mass_list) == len(pseudo_file_list)
    lines = "ATOMIC_SPECIES\n"
    for idx, ele in enumerate(label_list):
        lines += f"{ele} {mass_list[idx]} {pseudo_file_list[idx]}\n"
    return lines


def generate_numerical_orbital_lines(stru_para_dict):
    # NUMERICAL_ORBITAL lines
    raise NotImplementedError


def generate_lattice_constant_lines(stru_para_dict):
    # LATTICE_CONSTANT lines
    return f"LATTICE_CONSTANT\n{stru_para_dict['lattice_constant'] * Angstrom / Bohr}\n"


def generate_lattice_vectors_lines(stru_para_dict):
    # LATTICE_VECTORS lines
    lat_vec = stru_para_dict["lattice_matrix"]
    if isinstance(lat_vec, list):
        if len(lat_vec) == 3:
            return f"{lat_vec[0][0]} {lat_vec[0][1]} {lat_vec[0][2]}\n" + \
                   f"{lat_vec[1][0]} {lat_vec[1][1]} {lat_vec[1][2]}\n" + \
                   f"{lat_vec[2][0]} {lat_vec[2][1]} {lat_vec[2][2]}\n"
        else:
            raise ValueError(f"stru_para_dict[\"lattice_matrix\"] is list and has wrong shape: {len(lat_vec)}*({len(lat_vec[0])},{len(lat_vec[1])},{len(lat_vec[2])}).")
    elif isinstance(lat_vec, np.ndarray):
        assert lat_vec.shape == (3, 3)
        return "LATTICE_VECTORS\n" \
               f"{lat_vec[0][0]} {lat_vec[0][1]} {lat_vec[0][2]}\n" + \
               f"{lat_vec[1][0]} {lat_vec[1][1]} {lat_vec[1][2]}\n" + \
               f"{lat_vec[2][0]} {lat_vec[2][1]} {lat_vec[2][2]}\n"


def generate_atomic_positions_lines(stru_para_dict):
    # ATOMIC_POSITIONS lines
    lines = "ATOMIC_POSITIONS\n"
    coordinate_type = stru_para_dict["coordinate_type"]
    if coordinate_type == "Cartesian" or "Direct":
        lines += f"{coordinate_type}\n\n"
    else:
        raise KeyError(f"Unknown `coordinate_type`: {coordinate_type}.")
    atom_type_list = stru_para_dict["atom_type_list"]
    magnetism_list = stru_para_dict["magnetism_list"]
    number_of_atoms_list = stru_para_dict["number_of_atoms_list"]
    pos_list = stru_para_dict["pos_list"]
    # each element
    for idx, ele in enumerate(atom_type_list):
        lines += f"{ele}\n"
        lines += f"{magnetism_list[idx]}\n"
        lines += f"{number_of_atoms_list[idx]}\n"
        ele_num = int(number_of_atoms_list[idx])
        ele_pos_list = pos_list[idx]
        if isinstance(ele_pos_list, list):
            if len(ele_pos_list) == ele_num:
                for atom in ele_pos_list:
                    assert len(lines) == 6, "Atom position in ABACUS STRU file need 6 numbers."

                    lines += f"{atom[0]} {atom[1]} {atom[2]} {atom[3]} {atom[4]} {atom[5]}\n"
            else:
                raise ValueError(f"stru_para_dict[\"pos_list\"] is list and has wrong number: {len(lat_vec)} != ele_num of {atom}:{ele_num}.")
        elif isinstance(ele_pos_list, np.ndarray):
            assert ele_pos_list.shape == (ele_num, 6), f"Atom position in ABACUS STRU file need 6 numbers. Got {ele_pos_list.shape}."
            for atom in ele_pos_list:
                lines += f"{atom[0]} {atom[1]} {atom[2]} {int(atom[3])} {int(atom[4])} {int(atom[5])}\n"
    return lines


if __name__ == '__main__':
    write_abacus_stru(".", {
        "label_list": ["Si", "O"],
        "mass_list": ["1.000", "1.000"],
        "pseudo_file_list": ["Si.pz-vbc.UPF", "O.pz-vbc.UPF"],
        "lattice_constant": 10.2,  # Unit in Bohr, cif file unit is Angstrom!!!
        "lattice_matrix": np.array([
            [0.5, 0.5, 0.0],
            [0.5, 0.0, 0.5],
            [0.0, 0.5, 0.5]
        ]),
        "coordinate_type": "Cartesian",
        "atom_type_list": ["Si", "O"],
        "magnetism_list": [0.0, 0],
        "number_of_atoms_list": [2, 2],
        "pos_list": [np.array([
            [0, 0, 0, 0, 0, 0],
            [0.25, 0.25, 0.25, 1, 1, 1]
        ]),
            np.array([
                [0, 0, 0, 0, 0, 0],
                [0.25, 0.25, 0.25, 1, 1, 1]
            ])
        ]
    })
