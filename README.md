# Power Mean of 16S Data
## Introduction
This program will read a directory of 16S CSV files, split the taxonomy to the desired rank, sum assignments within the same V-region, then apply the specified power mean across the V regions for matching samples/ranks. The output is a combined feature table (by sample) of the format:

<center>

| taxonomy | S1 | S2  |
|----------|----|-----|
| g:A      | 25.25| 12.0 |
| g:B      | 80.0 | 120.50 |
| Assigned_Higher* | 0 | 50 |

</center>

Where g:A and g:B represent two different genera, and S1 and S2 represent two different samples. The numerical values in the cells correspond to the power mean counts. 

You may also have taxa that are not assigned to the rank specified, and these are combined into the "Assigned_Higher" feature.

## Getting Started
### Dependencies
You can install the dependencies using (virtual environment recommended):

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For the best results, ensure that your data is in the format specified in tests/example_data. You can have any number of V regions CSV files.

### Usage:

```
python3 main.py -d [path/to/data/dir] -r [column rank delimiter] -o [path/to/output/file.csv] -l [rank (e.g., "g")]
```

### Flags
| Flag | Description                                                                                                              |
|------|--------------------------------------------------------------------------------------------------------------------------|
| -d   | Path to input data directory. Should be in CSV format.                                                                   |
| -p   | The exp value to use. You can also specify inf for infinity.                                                             |
| -o   | Name and path to output relative to location where the script is being executed.                                         |
| -f   | If you data directory has more than one set of CSV files, you can input a regex expression to filter the filenames.      |
| -l   | Taxonomic rank. Use "g" for genus and "s" for species, etc. (default: "s")                                               |
| -r   | Regex to split the taxonomy ranks in the columns. Default=",".                                                           |
| -ec  | Extra cleaning of columns if your columns contain _V# as a suffix. (optional)                                            |
| -t   | If your data is transposed (i.e., row labels are sample ID and column labels are taxonomy), this will fix it. (optional) |

## Examples

To illustrate usage on the test data, run the following command.

```
python3 main.py -d tests/example_data/ex2 -p 1 -r "," -o test_output.csv -l g -f "v\d"
```

This will run the script on the data in `tests/example_data/ex2` on CSV files matching the `v\d` regex pattern. It will perform the splitting of taxonomic rank on a "," and then sort by the genus level. Finally, it will perform the power mean at `exp=1` and make a new file in the top-level directory called `test_output.csv`.

## Tests
If you want to be sure it is working, run the test with the following command:

```
pytest
```
In the `tests` directory, you will find `ex1`, which is two V regions with multiple samples, and `ex2` which is several V regions with one sample. 
