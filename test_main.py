import pandas as pd
from main import main
from unittest.mock import patch

expected_df = pd.read_csv("tests/example_data/expected_output.csv")


def cleanup():
    import os
    os.remove("tests/example_data/test_output.csv")


def test_main():
    with patch('sys.argv', ['main_test.py', '-d', 'tests/example_data', '-p', '1', '-r', ',', '-o', 'tests/example_data/test_output.csv', '-l', 's', '-f', r'v\d']):
        final_df, output = main()
        final_df.to_csv(output,
                        index_label="taxonomy")

        final_df_csv = pd.read_csv("tests/example_data/test_output.csv")
        assert (expected_df.equals(final_df_csv))

    cleanup()
