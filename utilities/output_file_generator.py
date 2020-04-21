# -*- coding: utf-8 -*-

import os
import sys
import numpy as np
import pandas as pd

d1 = os.path.abspath(os.path.join(os.path.split(sys.argv[0])[0],
                                  os.pardir, 'runs'))
file1 = os.path.abspath(os.path.join(os.path.split(sys.argv[0])[0],
                                     os.pardir, 'basic_gui',
                                     'NotionalETEOutput000.xlsx'))

delta = 0.05
mtypes = ['BRAVER', 'SOMERSAULT', 'ANGERMAX', 'HIGHWIND', 'HELLMASKER']
df = pd.read_excel(file1)
floatcols = [x for x in df.columns if df[x].dtype == 'float64']
nottime = [x for x in floatcols if x != 'time']
N = df.shape[0]

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
    # Generating temporary file
    df2 = df.copy(deep=True)

    # Making directory for files and filename for new file
    newdir = os.path.join(d1, f'run{num:03}')
    newfile = os.path.join(newdir, f'NotionalETEOutput{num:03}.xlsx')
    rcspath = os.path.join(newdir, 'rcs')
    os.makedirs(rcspath, exist_ok=True)

    # Making some numbers for substitution
    myversion = np.random.randint(0, 4)
    myID = np.random.randint(0, 500)

    # Missile type to substitute
    mtype = np.random.choice(mtypes)

    # Replacing missile metadata in the columns
    df2.datatype.replace('SAMP\d',f'{mtype}{myversion}',
                         regex=True, inplace=True)
    df2.datarec_id.replace('SAMP\d_\d',f'{mtype}{myversion}_{myID}',
                           regex=True, inplace=True)
    df2.datarec_id.replace('SAMP\d\.\d',f'{mtype}{myversion}_{myID}',
                           regex=True, inplace=True)
    df2.header_swmodel.replace('SAMP\d', f'{mtype}{myversion}',
                               regex=True, inplace=True)

    # Adds "noise" to each output file so it is familiar with
    # the original but will not match exactly
    for col in nottime:
        r = np.random.uniform(1 - delta, 1 + delta, N)
        df2[col] = df[col] * r
    df2.uniqueid = num
    df2.to_excel(newfile, index=False)


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
