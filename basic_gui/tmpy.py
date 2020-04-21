# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 07:57:40 2020

@author: white
"""


import os
import sys
import numpy as np

d1 = os.path.abspath(os.path.join(os.path.split(sys.argv[0])[0],
                                  os.pardir, 'runs'))
file1 = os.path.abspath(os.path.join(os.path.split(sys.argv[0])[0],
                                     'NotionalETEOutput000.xlsx'))

dirnums = np.array([
        55, 725, 939, 469, 969, 702, 584, 660, 293, 294, 380, 388, 835,
       192, 270, 388, 417, 117, 943, 873, 817, 388, 231, 622, 748, 627,
       341, 371, 358, 768, 328, 682, 107,  88, 403, 936, 601, 219, 626,
        48, 131,  90, 916, 770,  10, 262, 734, 841, 922,  63, 350, 329,
       707, 750, 871, 540, 790, 465, 710, 420, 338, 484, 814, 320, 644,
       517, 749, 417, 507, 186, 726, 831, 101, 382, 104, 166, 697, 666,
       480, 178, 741, 862, 516, 591, 893, 411, 152, 409, 611, 195,  65,
       999, 206, 601, 399, 321, 325, 253, 670, 404])

for num in dirnums:
    path = os.path.join(d1, f'run{num:03}', 'rcs')
    os.makedirs(path, exist_ok=True)


"""
import re
dir1 = 'C:\\Users\\white\\Documents\\etesim_gui_test\\basic_gui'
mfile_regex = r'NotionalETEOutput(\d+).xlsx'

files = []
for item in os.scandir(dir1):
    if item.is_file():
        check = re.match(mfile_regex, item.name)
        if check is not None:
            print(item.path)
"""
