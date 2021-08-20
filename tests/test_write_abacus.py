import pytest

import os
from bandapi.io.abacus.input import write_abacus_input


def test_write_input(tmpdir):
    input_name = "INPUT"
    input_dict = {
        "pseudo_dir": "./",
        "calculation": "scf",
        "ntype": 1,
        "nbands": 8,
        "basis_type": "pw",
        "symmetry": 0,
        "ecutwfc": 50,
        "dr2": 1.0e-7,
        "nstep": 1,
        "out_charge": 1
    }
    except_out = """INPUT_PARAMETERS
#Parameters (1.General)
pseudo_dir                    ./
calculation                   scf
ntype                         1
nbands                        8
symmetry                      0
#Parameters (2.PW)
ecutwfc                       50
dr2                           1e-07
out_charge                    1
#Parameters (3.Relaxation)
nstep                         1
#Parameters (4.LCAO)
basis_type                    pw
"""
    write_abacus_input(tmpdir, input_para_dict=input_dict, input_name=input_name)
    assert open(tmpdir / input_name).read() == except_out

def test_write_input_with_wrong_key(tmpdir):
    input_name = "INPUT"
    input_dict = {
        "pseudo_dir": "./",
        "calculation": "scf",
        "ntype": 1,
        "nbands": 8,
        "basis_type": "pw",
        "symmetry": 0,
        "ecutwfc": 50,
        "dr2": 1.0e-7,
        "nstep": 1,
        "out_charge": 1,
        "wrong_key":[]
    }
    with pytest.raises(KeyError) as e:
        write_abacus_input(tmpdir, input_para_dict=input_dict, input_name=input_name)
        assert isinstance(ImportError, e.type)