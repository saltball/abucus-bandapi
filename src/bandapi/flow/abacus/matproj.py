# -*- coding: utf-8 -*-
# ====================================== #
# @Author  : Yanbo Han
# @Email   : yanbohan98@gmail.com
# @File    : matproj.py
# ALL RIGHTS ARE RESERVED UNLESS STATED.
# ====================================== #
import glob
import pathlib
import shutil

import ase.data
import ase.symbols
import numpy as np
from bandapi.io.abacus.out import read_stru
from bandapi.third_part.matproj import MatProjWrapper
from dpdispatcher import Task

from bandapi.flow.abacus.flow import AbacusFlow
from bandapi.flow.task_content import NamedAtomsContentDict


class AbacusFlowFromMatProj(AbacusFlow):
    def __init__(
            self,
            API_KEY,
            machine,
            resource,
            task_flow_list,
            task_content,
            task_setup):
        """
        Setup an ABACUS workflow from data of material project.

        :param str API_KEY: Your Material Project API_KEY
        :param dict machine: Machine dict or str(for json file), same to dpdispatcher
        :param dict resource: Resource dict or str(for json file), same to dpdispatcher
        :param List[str] task_flow_list: str, for abacus flow kinds. Like scf, relax...
        :param Union[List] task_content: for id string of material project.
        :param dict task_setup: settings for task.
        """
        self.matprojwrapper = MatProjWrapper(API_KEY=API_KEY)
        assert self.matprojwrapper.test_connet()
        task_content = self.contentgenerate(task_content)
        super(AbacusFlowFromMatProj, self).__init__(
            machine=machine,
            resource=resource,
            task_flow_list=task_flow_list,
            task_content=task_content,
            task_setup=task_setup
        )

    def contentgenerate(self, task_content):
        content = {}
        for item in task_content:
            atoms = self.matprojwrapper.get_structure_by_id(item)
            content[item] = atoms[0]
        return NamedAtomsContentDict(content)
