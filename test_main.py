import pandas as pd
import numpy as np
from main import main
from unittest.mock import patch


def cleanup(path: str):
    import os
    os.remove(path)


def test_ex1():
    expected_df = pd.read_csv("tests/example_data/ex1/expected_output.csv")
    test_output = "tests/example_data/ex1/test_output.csv"
    with patch('sys.argv', ['main_test.py', '-d', 'tests/example_data/ex1', '-p', '1', '-r', ',', '-o', test_output, '-l', 'g', '-f', r'v\d']):
        final_df, output = main()
        final_df.to_csv(output,
                        index_label="taxonomy")

        final_df_csv = pd.read_csv("tests/example_data/ex1/test_output.csv")
        assert (expected_df.equals(final_df_csv))

    cleanup(test_output)


def test_ex2():
    expected_df = pd.read_csv("tests/example_data/ex2/expected_output.csv")
    test_output = 'tests/example_data/ex2/test_output.csv'
    with patch('sys.argv', ['main_test.py', '-d', 'tests/example_data/ex2', '-p', '1', '-r', ',', '-o', test_output, '-l', 'g', '-f', r'v\d+']):
        final_df, output = main()
        final_df.to_csv(output,
                        index_label="taxonomy")

        final_df_csv = pd.read_csv("tests/example_data/ex2/test_output.csv")

        # Isclose rather than equals because of rounding from the Excel export.
        assert (np.isclose(expected_df["O-001-02"],
                final_df_csv["O-001-02"]).all())

    cleanup(test_output)
