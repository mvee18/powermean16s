import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re
from scipy.stats import pmean

import sys
import argparse


def clean_csv(root, f, delimiter_pattern):
    print(f)

    df = pd.read_csv(os.path.join(root, f)).set_index('index')
    # Try to drop these columns if they exist. If they don't, continue.
    df.drop(columns=['even_stag', 'run', 'in_out',
            'v_region'], inplace=True, errors='ignore')
    # display(df)
    # display(df.T)

    new_cols = []
    cols = df.columns.to_list()
    for c in cols:
        pattern1 = re.compile(delimiter_pattern)
        col6 = re.split(pattern1, c)[-1]
        # print(col6)

        # pattern2 = re.compile(r'._\d_+')
        # col6_clean = re.split(pattern2, col6)[-1]

        if col6 == '__':
            new_cols.append("Unassigned")
            continue

        new_cols.append(col6)

    # print(new_cols)
    df.columns = new_cols
    deduped = df.groupby(lambda x: x, axis=1).sum()
    # display(deduped.T)

    return deduped.T


def extra_column_cleaning(df):
    cols = df.columns.to_list()
    new_cols = []
    for c in cols:
        pattern = re.compile(r'_V\d')
        splitted = re.split(pattern, c)
        new_cols.append(splitted[0])

    df.columns = new_cols
    return df


def coerce_exp(x):
    try:
        return int(x)
    except ValueError:
        if x == "inf":
            return np.inf
        else:
            raise argparse.ArgumentTypeError(
                "Invalid exponent value. Must be an int or 'inf'")


def pmean_df(data_dir: str, exp: int, file_pattern: str, delimiter_pattern: str):
    exp = coerce_exp(exp)

    cleaned_df = []

    for root, dirs, file in os.walk(data_dir):
        for f in file:
            if file_pattern in f:
                cleaned_df.append(clean_csv(root, f, delimiter_pattern))

    extra_clean = [extra_column_cleaning(df) for df in cleaned_df]
    # df1 = extra_clean[0].iloc[:, 0:8]
    # display(df1)
    # df2 = extra_clean[1].iloc[:, 0:8]
    # df3 = extra_clean[2].iloc[:, 0:8]

    # print(df1.shape)
    # print(df2.shape)
    # print(len(extra_clean))
    out = pd.concat(extra_clean, axis=0)
    # display(out)

    groups = out.groupby(level=0, axis=0)
    c = 0

    final = pd.DataFrame()
    for g in groups:
        # print(g[0])
        # display(g[1])
        m = pd.DataFrame(pmean(g[1], axis=0, p=exp, nan_policy='omit')).T
        m.columns = g[1].columns
        m.index = [g[0]]

        final = pd.concat([final, m], axis=0)

        # display(m)
        c += 1

    return final

# We need to have a flag for the data, the exponent of the power mean, and the output file.
# We can use getopt to parse the command line arguments.


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--data", help="The directory to the data. Must be in CSV format", required=True)
    parser.add_argument("-p", "--power", type=str,
                        help="The power to use for the power mean", required=True)
    parser.add_argument(
        "-r", "--regex", help="The regex to use for the data", required=True)
    parser.add_argument("-o", "--output", type=str,
                        help="specify the output file name")
    parser.add_argument("-f", "--file-id", type=str,
                        help="if more than one type of file in dir, use this to specify the sample identifier")
    parser.add_argument("-ec", "--extra-clean",
                        help="extra cleaning of columns ending with _V1, _V2, etc.", action="store_true")
    args = parser.parse_args()

    data = '/Volumes/TBHD/Bioinformatics/ion_torrent_qiime2_methods_manuscript/Classified_Tax_Counts_QIIME2_CSV_Files/Cutprimers/Species'

    output = pmean_df(data_dir=data, exp=args.power,
                      file_pattern="Silva", delimiter_pattern=args.regex)
    output.to_csv("test.csv")
