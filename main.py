import numpy as np
import pandas as pd
import os
import re
from scipy.stats import pmean
import argparse

taxonomic_levels = {"k": 0, "p": 1, "c": 2, "o": 3, "f": 4, "g": 5, "s": 6}


def fix_index(df: pd.DataFrame, index_col: int) -> pd.DataFrame:
    """
    This function fixes the index of the dataframe to be the given index column. Columns to the left of the index column are dropped.
    Parameters:
        df: the dataframe to fix
        index_col: the column to use as the index
    Returns:
        df: the fixed dataframe
    """
    if index_col == 0:
        df.set_index(df.columns[0], inplace=True)
        df.drop(columns=['even_stag', 'run',
                'in_out', 'v_region'], inplace=True)
        return df

    else:
        df = df.iloc[:, index_col:]
        df.set_index(df.columns[0], inplace=True)
        return df


def determine_taxonomic_rank(split_classification: list, taxon_level: str) -> str:
    """
    This function will take the split classification list and return the taxonomic rank specified by the taxon_level parameter.
    """
    if len(split_classification) == taxonomic_levels[taxon_level]+1:
        return split_classification[-1]
    else:
        return "Assigned_Higher"


def clean_columns(df: pd.DataFrame, delimiter_pattern=";", transpose=False, taxon_level="g"):
    """
    This function will clean the columns of the dataframe by splitting the column names on the delimiter pattern,
    and then using the determine_taxonomic_rank function to determine the taxonomic rank to use.
    """
    new_labels = []
    data = []
    if transpose:
        data = df.columns.to_list()
    else:
        data = df.index.to_list()

    for c in data:
        pattern1 = re.compile(delimiter_pattern)
        col6 = re.split(pattern1, c)

        org_name = determine_taxonomic_rank(col6, taxon_level)

        if org_name == '__' or org_name == f'{taxon_level}__':
            new_labels.append("Assigned_Higher")
            continue

        new_labels.append(org_name)

    if transpose:
        df.columns = new_labels
        return df
    else:
        df.index = new_labels
        return df


def clean_csv(root, f, delimiter_pattern=";", transpose=False, index_col=0, taxon_level="g"):
    """
    This function will clean the csv file by fixing the index, cleaning the columns, and then returning the cleaned dataframe. 
    If it needs to be transposed, it will be transposed.
    """
    path = os.path.join(root, f)
    if path.endswith(".csv"):
        df = pd.read_csv(os.path.join(root, f))
    elif path.endswith(".tsv"):
        df = pd.read_csv(os.path.join(root, f), sep="\t")

    df = fix_index(df, index_col)

    clean_columns(df, delimiter_pattern, transpose, taxon_level)

    if transpose:
        deduped = df.groupby(lambda x: x, axis=1).sum()
        return deduped.T

    else:
        deduped = df.groupby(lambda x: x, axis=0).sum()
        return deduped


def extra_column_cleaning(df):
    """
    This function will remove the _V# suffix from the column names if specified.
    """
    cols = df.columns.to_list()
    new_cols = []
    for c in cols:
        pattern = re.compile(r'_V\d')
        splitted = re.split(pattern, c)
        new_cols.append(splitted[0])

    df.columns = new_cols
    return df


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--data", help="The directory to the data. Must be in CSV format", required=True)
    parser.add_argument("-p", "--power", type=str,
                        help="The power to use for the power mean", required=True)
    parser.add_argument(
        "-r", "--regex", help="The regex to use for the data", default=",", required=True)
    parser.add_argument("-o", "--output", type=str,
                        help="specify the output file name", required=True)
    parser.add_argument("-f", "--file-id", type=str,
                        help="if more than one type of file in dir, use this to specify the sample identifier", default="(.*?)")
    parser.add_argument("-ec", "--extra-clean",
                        help="extra cleaning of columns ending with _V1, _V2, etc.")
    parser.add_argument("-t", "--transpose",
                        help="if the taxonomy is the column headers, use this flag. See tests/example_data for data as row names.")
    parser.add_argument("-l", "--taxon-level", type=str, default="g",
                        help="the taxonomic level to use for the data. options: k, p, c, o, f, g, s. default: g")
    return parser.parse_args()


def coerce_power(n: str):
    try:
        return int(n)
    except ValueError:
        if n == "inf":
            return np.inf
        raise Exception("Invalid power")


def concat_arrays(arrays: list, power: int):
    out = pd.concat(arrays, axis=0)

    groups = out.groupby(level=0, axis=0)

    final = pd.DataFrame()
    for g in groups:
        m = pd.DataFrame(pmean(g[1], axis=0, p=power, nan_policy='omit')).T
        m.columns = g[1].columns
        m.index = [g[0]]

        final = pd.concat([final, m], axis=0)

    final.rename_axis("taxonomy", inplace=True)
    return final
    # final.to_csv(output_file, index_label="taxonomy")


def main():
    args = parse_args()

    data, power, regex, output, file_id, extra_clean, rank = args.data, args.power, args.regex, args.output, args.file_id, args.extra_clean, args.taxon_level

    power = coerce_power(power)

    cleaned_dfs = []

    for root, dirs, file in os.walk(data):
        for f in file:
            if re.search(file_id, f):
                print(f)
                cleaned_dfs.append(clean_csv(root, f, delimiter_pattern=regex,
                                             transpose=False, index_col=1, taxon_level=rank))
    if extra_clean:
        extra_clean = [extra_column_cleaning(df) for df in cleaned_dfs]
        final = concat_arrays(extra_clean, power)
        return final, output
    else:
        final = concat_arrays(cleaned_dfs, power)
        return final, output


# Separate the main function from the rest of the code so that it can be imported in test.
if __name__ == "__main__":
    final, output = main()
    final.to_csv(output, index_label="taxonomy")
