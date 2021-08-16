# -*- coding: utf-8 -*-
# ====================================== #
# @Author  : Yanbo Han
# @Email   : yanbohan98@gmail.com
# @File    : flowtest.py
# ALL RIGHTS ARE RESERVED UNLESS STATED.
# ====================================== #

import pathlib

from bandapi.flow.abacus.matproj import AbacusFlowFromMatProj

ABACUS_COMMAND = r"/home/ubuntu/abacus-develop/build/abacus"
CPU_NUM = 8
API_KEY = ""
LOCAL_ROOT = pathlib.Path(r"./dispatcher")

machine = {
    "batch_type": "shell",
    "context_type": "SSHContext",
    "local_root": LOCAL_ROOT.as_posix(),
    "remote_root": "/home/ubuntu/work/dispatcher",  # SETUP THIS
    "remote_profile": {
        "hostname": "",
        "username": "ubuntu",
        "password": "",
        "port": 22,
        "timeout": 10

    }
}

resource = {
    "number_node": 1,
    "cpu_per_node": CPU_NUM,
    "group_size": 500
}

taskid = [
    # "mp-47",
    "mp-66",
    # "mp-149"
]

# One can modify workflow by change methods of AbacusFlowFromMatProj:
# - flow control conditions:
# `run_end`,`submit_loop_condition` for two phases and whether it's time to next phase. Effect how task work in flow.
# - calculation details:
# `get_band_kpt_array`: get atoms and return kpathlines like [[0,0,0,20],...] , see `get_band_kpt_args` for more. Use in `band` flow. Effect file KPT.
#       now we use `path` from ase.cell.bandpath
# `get_relax_kpt_array`: get lattice vector and return kpoint density like [4 4 4 0 0 0] for `relax` and `scf` flow. Effect file KPT.
#       now we use `kpt` simply by np.around(1/lat_vec.min=range)


flow = AbacusFlowFromMatProj(
    API_KEY=API_KEY,
    machine=machine,
    resource=resource,
    task_flow_list=["relax","scf-charge","nscf-band","band-data"],
    task_content=taskid,
    task_setup={
        "potential_name": "SG15",
        "dr2": 1.0e-6,
        "kpointscope": 3,
        "ecutwfc": 80,
        "remote_command": ABACUS_COMMAND,
        "kpathrange": 10,
        "flow_work_root": LOCAL_ROOT,
        "submission_check_period": 1,
        "nstep": 10
    }
)

flow.submit()
