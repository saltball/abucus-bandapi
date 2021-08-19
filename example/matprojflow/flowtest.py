# -*- coding: utf-8 -*-
# ====================================== #
# @Author  : Yanbo Han
# @Email   : yanbohan98@gmail.com
# @File    : flowtest.py
# ALL RIGHTS ARE RESERVED UNLESS STATED.
# ====================================== #

import pathlib

import dpdispatcher
import paramiko.ssh_exception
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

taskPath = pathlib.Path(r"taskid.txt")  # no space line.
if taskPath.exists():
    taskid = taskPath.read_text().split("\n")
else:
    raise FileNotFoundError

# taskid = [        # Uncomment this to override taskid
#     "mp-47",
#     "mp-66",
#     "mp-149"
# ]

while 1:
    try:
        for smalllist in taskid:
            if (pathlib.Path(r"lock")/smalllist in list(pathlib.Path(r"lock").iterdir())):
                continue
            else:
                (pathlib.Path(r"lock")/smalllist).touch()
            flow = AbacusFlowFromMatProj(
                API_KEY=API_KEY,
                machine=machine,
                resource=resource,
                task_flow_list=[
                    # "relax",
                    "scf-charge",
                    "nscf-band",
                    # "band-data"
                ],
                task_content=[smalllist],
                task_setup={
                    "potential_name": "SG15",
                    "dr2": 1.0e-6, # dr2 parameter of ABACUS, see its document.
                    "kpointscope": 5, # kpoint density for scf calculation. This number will be used for the smallest one of the three density, other number will be calculated due to lattice vector.
                    "ecutwfc": 70, # ecutwfc parameter of ABACUS, see its document
                    "remote_command": ABACUS_COMMAND, # see above comment
                    "kpathrange": 15, # kpath density of band-structure calculation (only).
                    "flow_work_root": LOCAL_ROOT, # local path of flow
                    "submission_check_period": 1, # check time of tasks.
                    # "nstep": 10,
                    "clean": False, # if False, file on remote server won't be delete by dpdispatcher after calculations.(For frequently stop and unstable network connection.)
                    "kpointfix":True # if True, kpoint with will be fix as Gamma:[kpointscope,kpointscope,kpointscope]
                }
            )

            flow.submit()
            (pathlib.Path(r"lock") / smalllist).unlink()
    except paramiko.ssh_exception.SSHException:
        pass

