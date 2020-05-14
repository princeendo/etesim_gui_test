# -*- coding: utf-8 -*-

import os
import sys
import numpy as np
import pandas as pd

# These polynomials may be used to generate the lat/lon values necessary
# to produce a value x kilometers away from an object
polylat = np.array([9.00818164e-03, 9.90032277e-06])
polylon = np.array([1.15326279e-02, -3.91292661e-06])

# The increments in latitude and longitude to move 1km
km_lat = 0.009008789934838205
km_lon = 0.011532453269674078

default_ecef = np.array([1116578.706, 4841123.275, 3985227.184])
default_lla = np.array([38.92261772, 77.0121658, -652.68192316])


def randomAsset(run_number,
                baseLLA=np.array([38.92261772, 77.0121658, -652.68192316]),
                kmdiff=1, move=True, position='random'):

    lat, lon, alt = baseLLA
    if move:
        if position == 'random':
            position = np.random.choice(['none', 'north', 'south',
                                         'east', 'west'])
        if position == 'north':
            lat += (kmdiff * km_lat)
        elif position == 'south':
            lat -= (kmdiff * km_lat)
        elif position == 'east':
            lon += (kmdiff * km_lon)
        elif position == 'west':
            lon -= (kmdiff * km_lon)

    categories = ['Launcher', 'Radar']

    names = {'Radar': ['NICK', 'Sentinel', 'Patriot'],
             'Launcher': ['Launcher'], }

    category = np.random.choice(categories)
    name = np.random.choice(names[category])

    id_ = np.random.randint(1000, 10000)

    return (category, name, id_, run_number, (lat, lon, alt))


def makeAssets(numAssets, run_number):
    return (randomAsset(run_number) for _ in range(numAssets))


def writeAssets(outFile, assetList):
    with open(outFile, 'w') as out:
        for asset in assetList:
            category, name, uniqueID, run_number, lla = asset
            string_ = stringAsset(category, name, uniqueID,
                                  run_number, lla=lla)
            out.write(string_)


def stringAsset(category, name, uniqueID, run, *,
                ecef=None, lla=None, enu=None):

    # Guarantees at least one of the keywords is not None
    allNone = ecef is None and lla is None and enu is None
    assert(not allNone)

    asset = (f'# Asset\n'
             f'Category:   {category}\n'
             f'Name:       {name}\n'
             f'UniqueID:   {uniqueID}\n'
             f'Run:        {run}\n'
             )

    if ecef is not None:
        asset += 'ECEF XYZ:   ' + ' '.join(map(str, ecef)) + '\n'
    if lla is not None:
        asset += 'LatLonAlt:  ' + ' '.join(map(str, lla)) + '\n'
    if enu is not None:
        asset += 'ENU:        ' + ' '.join(map(str, enu)) + '\n'

    return asset


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
    generateMissileOutput(d2, file1,)
    generateAssetOutput(d2, file2,)


def generateAssetOutput(outDir, assetFile,
                        dirnums=np.array([954, 971, 708, 443, 947])):

    for k, dirNum in enumerate(dirnums):
        numAssets = np.random.randint(1, 5)
        newdir = os.path.join(outDir, f'run{dirNum:03d}')
        newFile = os.path.join(newdir, 'assets.txt')
        newAssets = makeAssets(numAssets, dirNum)
        writeAssets(newFile, newAssets)

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
