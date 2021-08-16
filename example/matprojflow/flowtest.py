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


flow = AbacusFlowFromMatProj(
    API_KEY=API_KEY,
    machine=machine,
    resource=resource,
    task_flow_list=[
        # "scf-charge",
        # "nscf-band",
        "band-data"
    ],
    task_content=taskid,
    task_setup={
        "potential_name": "SG15",
        "dr2": 1.0e-7,
        "kpointscope": 5,
        "ecutwfc": 80,
        "remote_command": ABACUS_COMMAND,
        "kpathrange": 20,
        "flow_work_root": LOCAL_ROOT,
        "submission_check_period": 1,
        "nstep": 10
    }
)

flow.submit()
