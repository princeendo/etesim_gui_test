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

dirnums = np.array([954, 971, 708, 443, 947, 483, 390, 582, 184, 973])

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
        r = np.random.normal(loc=1, scale=0.3)
        df2[col] = df[col] * r
    df2.uniqueid = num
    df2.to_excel(newfile, index=False)
