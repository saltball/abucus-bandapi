# -*- coding: utf-8 -*-
# ====================================== #
# @Author  : Yanbo Han
# @Email   : yanbohan98@gmail.com
# @File    : kpt.py
# ALL RIGHTS ARE RESERVED UNLESS STATED.
# ====================================== #

import pathlib
AbacusKPTKeyDict={
    "K_POINTS": {
        "number_of_kpt",
    },
    # 0 means generate automatically
    "method": {
        "mode",
        "content",
    }
}

AbacusKptBlock = {
    "number_of_kpt": "K_POINTS",
    "mode": "method",
    "content": "method",
}


def write_abacus_kpt(
        task_root: str,
        kpt_para_dict: dict
):
    all_kpt_keys = kpt_para_dict.keys()
    kpt_blocks = set()

    for key in all_kpt_keys:
        try:
            kpt_blocks.add(AbacusKptBlock[key])
        except KeyError:
            raise KeyError(f"Invalid kpt Key for ABACUS: {key}")

    with open(pathlib.Path(task_root) / "KPT", "w") as f:
        print("K_POINTS", file=f)
        number_of_kpt = int(kpt_para_dict["number_of_kpt"])
        print(number_of_kpt, file=f)
        if number_of_kpt == 0:  # generate automatically
            print(generate_kpt_with_MP(kpt_para_dict), file=f)
        elif number_of_kpt > 0:
            print(generate_kpt_manually(kpt_para_dict), file=f)
        else:
            ValueError(f"What's the number_of_kpt {number_of_kpt} mean?")


def generate_kpt_with_MP(kpt_para_dict):
    lines = ""
    if kpt_para_dict["mode"] == "Gamma":
        lines += "Gamma\n"
    elif kpt_para_dict["mode"] == "MP":
        lines += "MP\n"
    else:
        KeyError(f"Invalid kpt method Key for Monkhorst-Pack method in ABACUS: {key}. It should be `Gamma' or `MP'")

    kpt_mode_content = kpt_para_dict["content"]
    if isinstance(kpt_mode_content, list):
        assert len(kpt_mode_content) == 6, "kpt_mode_content position in ABACUS KPT file need 6 numbers."
        lines += f"{kpt_mode_content[0]} {kpt_mode_content[1]} {kpt_mode_content[2]} {kpt_mode_content[3]} {kpt_mode_content[4]} {kpt_mode_content[5]}\n"
    elif isinstance(kpt_mode_content, np.ndarray):
        assert kpt_mode_content.shape == (6,), f"kpt_mode_content in ABACUS KPT file need 6 numbers and no more dimensions. Got {kpt_mode_content.shape}."
        lines += f"{int(kpt_mode_content[0])} {int(kpt_mode_content[1])} {int(kpt_mode_content[2])} {int(kpt_mode_content[3])} {int(kpt_mode_content[4])} {int(kpt_mode_content[5])}\n"
    return lines

def generate_kpt_manually(kpt_para_dict):
    lines = ""
    calculate_band=False
    if kpt_para_dict["mode"] == "Direct":
        lines += "Direct\n"

    elif kpt_para_dict["mode"] == "Cartesian":
        lines += "Cartesian\n"

    elif kpt_para_dict["mode"] == "Line":
        lines += "Line\n"
        calculate_band=True
    elif kpt_para_dict["mode"] == "Line_Cartesian":
        lines += "Line_Cartesian\n"
        calculate_band = True
    else:
        KeyError(f"Invalid kpt method Key for manual method in ABACUS: {key}. It should be `Direct' and `Cartesian' for explicitly k-point, or 'Line' and 'Line_Cartesian' for band-structure calculations")

    kpt_mode_content = kpt_para_dict["content"]
    kpt_num=int(kpt_para_dict["number_of_kpt"])
    if calculate_band:
        if isinstance(kpt_mode_content, list):
            if len(kpt_mode_content) == kpt_num:
                for content_line in kpt_mode_content:
                    assert len(content_line) == 4, f"Each kpt_mode_content in ABACUS KPT file need 4 numbers when using method {kpt_para_dict['mode']}."
                    lines += f"{content_line[0]} {content_line[1]} {content_line[2]} {content_line[3]}\n"
            else:
                raise ValueError(f"kpt_mode_content[\"content\"] is list and has wrong shape: {len(lat_vec)} != ele_num of {atom}:{kpt_num}.")
        elif isinstance(kpt_mode_content, np.ndarray):
            assert kpt_mode_content.shape == (kpt_num,4), f"kpt_mode_content in ABACUS KPT file need 4 numbers and {kpt_num} lines when using method {kpt_para_dict['mode']}. Got {kpt_mode_content.shape}."
            for content_line in kpt_mode_content:
                lines += f"{int(content_line[0])} {int(content_line[1])} {int(content_line[2])} {int(content_line[3])}\n"
        else:
            raise TypeError(f"Except list or np.ndarray for kpt_mode_content, got {type(kpt_mode_content)} instead.")
    else:
        raise NotImplementedError("Explicitly k-point is not ready for use.")
    return lines

if __name__ == '__main__':
    write_abacus_kpt(".",
                     kpt_para_dict={
                             "number_of_kpt":0,
                             "mode":"Gamma",
                             "content":[2,2,2,0,0,0],
                     })
    input()
    write_abacus_kpt(".",
                     kpt_para_dict={
                             "number_of_kpt":6,
                             "mode":"Line",
                             "content":[
                                 [0.5, 0.0, 0.5, 20],
                                 [0.0, 0.0, 0.0, 20],
                                 [0.5, 0.5, 0.5, 20],
                                 [0.5, 0.25, 0.75, 20],
                                 [0.375,0.375, 0.75,20],
                                 [0.0, 0.0, 0.0,1]
                             ],
                     })
