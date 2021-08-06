# -*- coding: utf-8 -*-
# ====================================== #
# @Author  : Yanbo Han
# @Email   : yanbohan98@gmail.com
# @File    : __init__.py.py
# ALL RIGHTS ARE RESERVED UNLESS STATED.
# ====================================== #
import hashlib
import pathlib
from typing import Union


#
# class IOFile:
#     def __init__(
#             self,
#             filepath: Union[str, pathlib.Path],
#             mode="r"
#     ):
#         self._mode=self._check_mode(mode)
#         self.filepath = filepath
#         self._refresh_id()
#
#     def _refresh_id(self):
#         if not pathlib.Path(filepath).exists():
#             self._id = None
#         else:
#             self._id = self.get_hash()
#     def _check_mode(self,mode):
#         if mode=="r":
#             return "r"
#         elif mode=="w":
#             return "w"
#         else:
#             raise ValueError(f"Unknown mode {mode}.")
#
#     @property
#     def mode(self):
#         if self._mode:
#             return self._check_mode(self._mode)
#         else:
#             raise NotImplementedError
#
#     def id(self):
#         if self._id:
#             return self._id
#         else:
#             self._refresh_id()
#             if not self._id:
#                 raise NotImplementedError
#
#     def get_hash(self):
#         with open(self.filepath, "rb") as f:
#             sha1obj = hashlib.sha1()
#             sha1obj.update(f.read())
#             hash = sha1obj.hexdigest()
#             return hash
#
#     @property
#     def info_dict(self) -> dict:
#         """
#         File infomation dict. Must Implement by `parse_file().`
#         """
#         if hasattr(self, "_info_dict"):
#             return self._info_dict
#         else:
#             try:
#                 self.parse_file()
#             except NotImplementedError:
#                 raise("`_info_dict` must be implemented in `input_configure()`.")
#
#     def parse_file(self) -> dict:
#         if self.mode=="w":
#             raise NotImplementedError("`_parse_file()` is not implemented when mode='r'.")
#
#
# class InputFile(IOFile):
#     """
#     One should implement three methods for InputFile class: `parse_file`(to read file),`input_configure`,`write_file`(to write file)
#     """
#     def __init__(
#             self,
#             filepath: Union[str, pathlib.Path],
#             mode="r"
#     ):
#         super(InputFile, self).__init__(filepath=filepath,mode=mode)
#
#     def configure(self, configure_dict: dict, notwrite: bool = False):
#         """
#
#         :param configure_dict:
#         :param notwrite: Set to True to avoid write file.
#         :return:
#         """
#         self.input_configure(configure_dict)
#         if not notwrite:
#             self.write_file()
#
#     def input_configure(self, configure_dict) -> None:
#         raise NotImplementedError("`input_configure` must be implemented.")
#
#     def write_file(self) -> None:
#         raise NotImplementedError("`write_file` must be implemented.")
#
#
# class OutputFile(IOFile):
#     def __init__(
#             self,
#             filepath: Union[str, pathlib.Path]
#     ):
#         super(OutputFile, self).__init__(filepath=filepath,mode="r")
