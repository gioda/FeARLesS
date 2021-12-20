#!/usr/bin/env python
#
# @Author: Giovanni Dalmasso <gio>
# @Date:   15-Dec-2021
# @Email:  giovanni.dalmasso@embl.es
# @Project: FeARLesS
# @Filename: utils.py
# @Last modified by:   gio
# @Last modified time: 15-Dec-2021
# @License: MIT
# @Copyright: Copyright © 2021 Giovanni Dalmasso

import os
from vedo import printc
import shutil
from sys import exit


def confirm(message):
    """
    Ask user to enter Y or N (case-insensitive).

    :return: True if the answer is Y.
    :rtype: bool
    """
    answer = ""
    while answer not in ["y", "n"]:
        answer = input(message).lower()
    return answer == "y"


def pathExists(path):
    if not os.path.exists(path):
        os.mkdir(path)
        printc("Directory ", path, " Created ", c='green')
    else:
        printc("Directory ", path, " already exists", c='red')
        if confirm("Should I delete the folder and create a new one [Y/N]? "):
            shutil.rmtree(path)
            os.mkdir(path)
            printc("Directory ", path, " Created ", c='green')
        else:
            exit()
