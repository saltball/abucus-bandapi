# -*- coding: utf-8 -*-
# ====================================== #
# @Author  : Yanbo Han
# @Email   : yanbohan98@gmail.com
# @File    : matproj.py
# ALL RIGHTS ARE RESERVED UNLESS STATED.
# ====================================== #
import urllib.request

import ase.io.vasp
import pymatgen.core.structure
from typing import List

USE_PYMATGEN=False
try:
    from pymatgen.ext.matproj import MPRester
    USE_PYMATGEN=True
except ImportError:
    pass

MatProjAPIUrl="https://www.materialsproject.org/rest/v2/materials/{}/vasp?API_KEY={}"

class MatProjWrapper:
    def __init__(self, API_KEY, force_not_use_pymatgen=False):
        self.API_KEY=API_KEY
        if USE_PYMATGEN and not force_not_use_pymatgen:
            self.mprester=MPRester(API_KEY)
            self.USE_PYMATGEN=True
        else:
            self.USE_PYMATGEN=False

    def get_structure_by_id(self,id):
        if self.USE_PYMATGEN:
            return self._result_wrapper(self.mprester.get_structure_by_material_id(id), _pymatgen=True)
        else:
            url=MatProjAPIUrl.format(id,self.API_KEY)
            url=urllib.request.Request(url,headers = {'User-Agent':'Mozilla/5.0 3578.98 Safari/537.36'})
            result = urllib.request.urlopen(url)
            return self._result_wrapper(result, _pymatgen=False)

    def _result_wrapper(self, result, _pymatgen)->List[ase.atoms.Atoms]:
        """
        Deal with different result using or not using pymatgen.
        :param result: List[ase.atoms.Atom()], generally be len()==1
        :param _pymatgen: bool
        :return:
        """
        if _pymatgen:
            _, fname = tempfile.mkstemp(text=True)
            with open(fname, "w") as f:
                f.write(result.to("poscar"))
            return ase.io.read(fname,index=':',format="vasp")
        else:
            import json
            result = json.load(result)
            if result["valid_response"]:
                _, fname = tempfile.mkstemp(text=True)
                with open(fname, "w") as f:
                    f.write(result["response"][0]["cif"])
                return ase.io.read(fname, index=':', format="cif")
            elif not result["api_key_valid"]:
                raise ValueError(f"Invalid API_KEY: {self.API_KEY}. Check your API_KEY at https://www.materialsproject.org/open!")



if __name__ == '__main__':
    import json
    from pprint import pprint
    import tempfile
    from ase.visualize import view
    API_KEY = ""
    w = MatProjWrapper(API_KEY,force_not_use_pymatgen=True)
    result=w.get_structure_by_id("mp-1283030")
    print(result)
