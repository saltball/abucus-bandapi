# -*- coding: utf-8 -*-
# ====================================== #
# @Author  : Yanbo Han
# @Email   : yanbohan98@gmail.com
# @File    : __init__.py.py
# ALL RIGHTS ARE RESERVED UNLESS STATED.
# ====================================== #

default_settings = {
    "ecutwfc": 80,
    "dr2": 1.0e-7,
    "kpointscope": 3,
    "kpathscope": 20,
    "nstep":20
}

from bandapi.flow.abacus.calculation_state import *
from bandapi.flow.abacus.result_state import *
