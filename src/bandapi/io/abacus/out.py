# -*- coding: utf-8 -*-
# ====================================== #
# @Author  : Yanbo Han
# @Email   : yanbohan98@gmail.com
# @File    : out.py
# ALL RIGHTS ARE RESERVED UNLESS STATED.
# ====================================== #
import pathlib
import re

import numpy as np
from ase.atoms import Atoms
from ase.units import Angstrom, Bohr

BandPointPattern = re.compile(r"k-points(.*\d)")
BandValuePattern = re.compile(r"spin[\d+]_final_band(.*\d)")
EFermi_Pattern = re.compile(r"E_Fermi(.*\d)")


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


def read_band_in_log(log_file, atoms=None, _nspin=1, outputfile=None):
    """

    :param log_file:
    :param int _nspin:
    :Warning: _nspin is not used.
    :return: kpathArray,bandArray
    """
    with open(log_file, "r") as f:
        content = f.readlines()
    # match
    kpath = []
    bandValue = BandValuePattern.findall("".join(content))
    with open(log_file, "r") as f:
        line = f.readline()
        while line:
            if "nkstot" in line:
                knum = int(line.split("=")[-1])
                f.readline()
                f.readline()
                for kpoint_idx in range(knum):
                    kpoint_line = f.readline()
                    kpath.append(kpoint_line)
            else:
                pass
            line = f.readline()

    nband = len(bandValue) / knum
    assert nband == np.around(nband)
    nband = int(nband)
    # split
    kpathArray = list([item.split()[1:4] for item in kpath])
    bandArray = list([item.split()[_nspin] for item in bandValue])

    kpathArray = np.array(kpathArray, dtype=float)
    bandArray = np.array(bandArray, dtype=float).reshape([_nspin, knum, -1])
    if outputfile:
        file = pathlib.Path(outputfile)
        if pathlib.Path(file).exists():
            file.unlink()
        with open(file, "a")as f:
            for idx_band in range(knum):
                kpathBandValue = "".join(str(item) + " " for item in bandArray[0, idx_band])
                print(f"{idx_band + 1} {kpathBandValue}", file=f)
    return kpathArray, bandArray


def read_fermi_energy_from_log(log_file):
    """
    Return the list of second value of ABACUS log, it should be unit as `eV`
    :param log_file:
    :return:
    """
    with open(log_file, "r") as f:
        content = f.readlines()
    ferimiValues = EFermi_Pattern.findall("".join(content))
    return list([float(item.split()[1]) for item in ferimiValues])
