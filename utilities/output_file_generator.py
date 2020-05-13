# -*- coding: utf-8 -*-

import os
import shutil
import sys
import numpy as np
import pandas as pd


def main():
    d1 = os.path.abspath(os.path.join(os.path.split(sys.argv[0])[0],
                                      os.pardir, '100runs'))
    d2 = os.path.abspath(os.path.join(os.path.split(sys.argv[0])[0],
                                      os.pardir, 'runs'))
    file1 = os.path.abspath(os.path.join(os.path.split(sys.argv[0])[0],
                                         os.pardir, 'basic_gui',
                                         'NotionalETEOutput000.xlsx'))
    file2 = os.path.abspath(os.path.join(os.path.split(sys.argv[0])[0],
                                         os.pardir, 'basic_gui',
                                         'notionalasset.txt'))
    generateMissileOutput(d2, file1)
    generateAssetOutput(d2, file2)


def generateAssetOutput(outDir, assetFile,
                        dirnums=np.array([954, 971, 708, 443, 947])):

    for k, dirNum in enumerate(dirnums):

        # Making directory for files and filename for new file
        newdir = os.path.join(outDir, f'run{dirNum:03}')
        newfile = os.path.join(newdir, 'assets.txt')
        if os.path.isfile(newfile):
            os.remove(newfile)
        shutil.copy2(assetFile, newfile)
    return


def generateMissileOutput(outDir, missileFile,
                          dirnums=np.array([954, 971, 708, 443, 947])):
    mtypes = ['BRAVER', 'SOMERSAULT', 'HIGHWIND', 'HELLMASKER']
    df = pd.read_excel(missileFile)
    floatcols = [x for x in df.columns if df[x].dtype == 'float64']
    notTime = [x for x in floatcols if x != 'time']

    # dirnums = np.array([954, 971, 708, 443, 947])
    # dirnums = np.arange(100)
    numShots = np.random.randint(1, 5, len(dirnums))

    for k, dirNum in enumerate(dirnums):

        # Making directory for files and filename for new file
        newdir = os.path.join(outDir, f'run{dirNum:03}')
        newfile = os.path.join(newdir, f'NotionalETEOutput{dirNum:03}.xlsx')
        rcspath = os.path.join(newdir, 'rcs')
        os.makedirs(rcspath, exist_ok=True)

        df2 = pd.concat((dummyDF(df, mtypes, dirNum, notTime)
                         for _ in range(numShots[k])))

        df2.to_excel(newfile, index=False)


def dummyDF(df, mtypes, dirNum, notTime):
    # Generating temporary DataFrame
    df2 = df.copy(deep=True)

    # Missile type to substitute
    mtype = np.random.choice(mtypes)

    # Instance for mtype
    myID = np.random.randint(0, 500)

    # Replacing missile metadata in the columns
    df2.datatype.replace('SAMP\d',f'{mtype}',
                         regex=True, inplace=True)
    df2.datarec_id.replace('SAMP\d_\d',f'{mtype}_{myID}',
                           regex=True, inplace=True)
    df2.datarec_id.replace('SAMP\d\.\d',f'{mtype}_{myID}',
                           regex=True, inplace=True)
    df2.header_swmodel.replace('SAMP\d', f'{mtype}',
                               regex=True, inplace=True)

    # Adds "noise" to each output file so it is familiar with
    # the original but will not match exactly
    for col in notTime:
        r = np.random.normal(loc=1, scale=0.000001)
        df2[col] = df[col] * r
    df2.uniqueid = dirNum

    return df2


if __name__ == "__main__":
    main()
