# -*- coding: utf-8 -*-
# ====================================== #
# @Author  : Yanbo Han
# @Email   : yanbohan98@gmail.com
# @File    : out.py
# ALL RIGHTS ARE RESERVED UNLESS STATED.
# ====================================== #

import numpy as np
from ase.atoms import Atoms
from ase.units import Angstrom, Bohr


def read_stru(stru_file):
    lat_const = None
    cell = []
    atom_list = []
    pos_type = None
    pos_list = []
    f = open(stru_file)
    content = f.readline()
    try:
        while content:
            if content.startswith("LATTICE_CONSTANT"):
                content = f.readline()
                lat_const = float(content) * Bohr / Angstrom
            elif content.startswith("LATTICE_VECTORS"):
                content = f.readline()
                cell.append(list(map(float, content.split()[:3])))
                content = f.readline()
                cell.append(list(map(float, content.split()[:3])))
                content = f.readline()
                cell.append(list(map(float, content.split()[:3])))
                cell = np.array(cell, dtype=np.double) * lat_const
            elif content.startswith("ATOMIC_POSITIONS"):
                content = f.readline()
                pos_type = content.split()[0]
                content = f.readline()
                while content:
                    if not content.isspace():
                        atom_name = content.split()[0]
                        content = f.readline()  # TODO:read magnetism
                        content = f.readline()
                        atom_num = int(content.split()[0])
                        for i in range(atom_num):
                            atom_list.append(atom_name)
                            content = f.readline()
                            pos_one = np.array(list(map(float, content.split()[:3])))
                            if pos_type == "Direct":
                                pos_list.append(pos_one @ cell)
                            elif pos_type == "Cartesian":
                                pos_list.append(pos_one * lat_const)
                            else:
                                raise NotImplementedError(f"Unknown ATOMIC_POSITIONS type: {pos_type}")
                        content = f.readline()
                    else:
                        content = f.readline()

            content = f.readline()
    except EOFError:
        pass
    atoms = Atoms(
        symbols=atom_list,
        positions=pos_list,
        cell=cell,
        pbc=True
    )
    return atoms
