# -*- coding: utf-8 -*-
# ====================================== #
# @Author  : Yanbo Han
# @Email   : yanbohan98@gmail.com
# @File    : task_content.py
# ALL RIGHTS ARE RESERVED UNLESS STATED.
# ====================================== #
import abc

import ase


class TaskContent(abc.ABC):
    def __init__(self,*args,**kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def __iter__(self):
        raise NotImplementedError

    @property
    def content_state(self):
        raise NotImplementedError

class NamedAtomsContentDict(dict, TaskContent):
    def __init__(self,atoms_dict:dict):
        """
        A wrapped dict in which make sure all atoms in dict is pbc.

        :param dict atoms_dict: atoms named with keys in dict.
        """
        dict.__init__({})
        self._check(atoms_dict)
        self.update(atoms_dict)

    def _check(self,atoms_dict):
        for k,v in atoms_dict.items():
            v:ase.Atoms
            if not v.pbc.any():
                raise TypeError(f"ase.Atoms {k} is not a proper pbc system. Check your data.")

    @property
    def content_state(self):
        return "Unknown"