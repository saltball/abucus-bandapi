# -*- coding: utf-8 -*-
# ====================================== #
# @Author  : Yanbo Han
# @Email   : yanbohan98@gmail.com
# @File    : potential.py
# ALL RIGHTS ARE RESERVED UNLESS STATED.
# ====================================== #
import json
import os
import pathlib
from typing import Union

PotentialNameAlias = {
    #SG15
    "SG15": "SG15",
    "SG15_ONCV": "SG15",
    "SG15_ONCV_V1.0": "SG15",
    "SG15_V1.0": "SG15"
}

PotentialDictFile = pathlib.Path(__file__).parent/r"pot_path.json"
PotentialDataDir = pathlib.Path(__file__).parent/r"potdata"


class AbacusPotential:
    def __init__(self, pot_name: str = "SG15"):
        """
        Hold potential files of ABACUS.
        Use `AbacusPotential(pot_name="SG15")["C"]` to get `absolute` path of SG15 potential to carbon.

        :param pot_name: Available potential: ["SG15"]
        """
        self.pot_name: str = self._pot_name_praser(pot_name)
        with open(PotentialDictFile, "r") as file:
            self.pot_dict: dict = json.load(file)[self.pot_name]
        self.pot_files: dict = self.pot_dict["file"]

    def __getitem__(self, key: Union[str, int]):
        if isinstance(key, int):
            try: #pragma: no cover
                from ase.atom import chemical_symbols
                key = chemical_symbols[key]
            except ImportError: #pragma: no cover
                raise RuntimeError("Please run `pip install ase` or `conda install ase -c conda-forge` to convert atom number to atom symbols")
        try:
            pot_file_name: str = self.pot_files[key]
            pot_file_name = PotentialDataDir/self.pot_dict["dir"]/pot_file_name
            return pot_file_name
        except KeyError:
            raise KeyError(f"There is no {self.pot_name} potential for element {key}.\nAvailable element for {self.pot_name}:{list(self.pot_files.keys())}")

    @staticmethod
    def _pot_name_praser(pot_name: str):
        pot_name = pot_name.upper()
        return PotentialNameAlias[pot_name]
