import json
from collections import defaultdict

import pandas as pd
import numpy as np


def intConverter(obj):
    if isinstance(obj, pd._libs.missing.NAType):
        return None
    elif isinstance(obj, pd.Int64Dtype):
        return int(obj)
    elif isinstance(obj, np.integer):
        return int(obj)


def getLabel(*elements, year, locatiepunt, d):

    labelelements = []
    for i in elements:

        if pd.isna(i):
            continue
        elif i:
            labelelements.append(str(i))

    label = " ".join(labelelements)

    if 'geometry' not in d[label][year]:
        d[label][year]['geometry'] = []

    if locatiepunt not in d[label][year]['geometry']:
        d[label][year]['geometry'].append(locatiepunt)

    return label


def main():
    # df = pd.read_csv('data/concordans.csv', low_memory=False)
    df = pd.read_excel(
        'data/concordans ATM 1943-1909-1853-1832 v22-10-2020.xlsx')
    df = df.where((pd.notnull(df)), None)
    df = df.astype({
        # '1943_huisnummer': 'Int64',
        '1909_huisnummer': 'Int64',
        '1876_huisnummer': 'Int64',
        '1853_buurtnummer': 'Int64',
        '1832_perceelnummer': 'Int64'
    })

    with open('data/name2adamlink.json') as infile:
        name2adamlink = json.load(infile)

    d = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

    for r in df.to_dict(orient='records'):

        locatiepunt = r['Locatiepunt v27-08-2020']

        # 1943
        if r['1943_straat']:

            label = getLabel(r['1943_straat'],
                             r['1943_huisnummer'],
                             r['1943_huisnummertoevoeging'],
                             year=1943,
                             locatiepunt=locatiepunt,
                             d=d)

            d[label][1943]['straat']['naam'] = r['1943_straat']
            d[label][1943]['straat']['adamlink'] = name2adamlink.get(
                r['1943_straat'])

            d[label][1943]['huisnummer'] = r['1943_huisnummer']
            d[label][1943]['huisnummertoevoeging'] = r[
                '1943_huisnummertoevoeging']

        # 1909
        if r['1909_straat']:

            label = getLabel(r['1909_straat'],
                             r['1909_huisnummer'],
                             r['1909_huisnummertoevoeging'],
                             locatiepunt=locatiepunt,
                             year=1909,
                             d=d)

            d[label][1909]['straat']['naam'] = r['1909_straat']
            d[label][1909]['straat']['adamlink'] = name2adamlink.get(
                r['1909_straat'])

            d[label][1909]['huisnummer'] = r['1909_huisnummer']
            d[label][1909]['huisnummertoevoeging'] = r[
                '1909_huisnummertoevoeging']

        # 1876
        if r['1876_straat']:

            label = getLabel(r['1876_buurt'],
                             r['1876_straat'],
                             r['1876_huisnummer'],
                             r['1876_huisnummertoevoeging'],
                             year=1876,
                             locatiepunt=locatiepunt,
                             d=d)

            d[label][1876]['straat']['naam'] = r['1876_straat']
            d[label][1876]['straat']['adamlink'] = name2adamlink.get(
                r['1876_straat'])

            d[label][1876]['huisnummer'] = r['1876_huisnummer']
            d[label][1876]['huisnummertoevoeging'] = r[
                '1876_huisnummertoevoeging']

            d[label][1876]['buurt']['naam'] = r['1876_buurt']
            d[label][1876]['buurt']['adamlink'] = name2adamlink.get(
                r['1876_buurt'])

        # 1853
        if r['1853_buurt']:

            label = getLabel('BUURT',
                             r['1853_buurt'],
                             r['1853_buurtnummer'],
                             r['1853_buurtnummertoevoeging'],
                             year=1853,
                             locatiepunt=locatiepunt,
                             d=d)

            d[label][1853]['buurt']['naam'] = r['1853_buurt']
            d[label][1853]['buurt']['adamlink'] = name2adamlink.get(
                r['1853_buurt'])

            d[label][1853]['buurtnummer'] = r['1853_buurtnummer']
            d[label][1853]['buurtnummertoevoeging'] = r[
                '1853_buurtnummertoevoeging']

        # 1832
        if r['1832_sectie']:

            label = getLabel('SECTIE',
                             r['1832_sectie'],
                             r['1832_perceelnummer'],
                             r['1832_perceelnummertoevoeging'],
                             year=1832,
                             locatiepunt=locatiepunt,
                             d=d)

            d[label][1832]['perceelsectie'] = r['1832_sectie']
            d[label][1832]['perceelnummer'] = r['1832_perceelnummer']
            d[label][1832]['perceelnummertoevoeging'] = r[
                '1832_perceelnummertoevoeging']

    with open('concordans.json', 'w', encoding='utf-8') as outfile:
        json.dump(d, outfile, indent=4, default=intConverter)

    # dcsv = []
    # for k, v in d.items():
    #     for year in v:
    #         data = dict()
    #         data['locatiepunt'] = k
    #         data['year'] = year

    #         for attribute in v[year]:
    #             if type(v[year][attribute]) != dict:
    #                 data[attribute] = v[year][attribute]
    #             else:
    #                 for attribute2 in v[year][attribute]:
    #                     if type(v[year][attribute][attribute2]) == str:
    #                         data[f"{attribute}_{attribute2}"] = v[year][
    #                             attribute][attribute2]
    #                     elif v[year][attribute][attribute2]:
    #                         print(v[year][attribute][attribute2])

    #         dcsv.append(data)

    # dfCSV = pd.DataFrame(dcsv)
    # dfCSV.head(10000).to_csv('concordansAdamlink.csv', index=False)


if __name__ == "__main__":
    main()
