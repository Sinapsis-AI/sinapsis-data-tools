# -*- coding: utf-8 -*-
import pandas as pd


def read_file(file: str) -> pd.DataFrame:
    """
    Reads a CSV file and returns its contents as a pandas DataFrame.

    Args:
        file (str): The path to the CSV file to be read.

    Returns:
        pd.DataFrame: The data from the CSV file as a pandas DataFrame.

    Raises:
        ValueError: If the file does not have a .csv extension.
    """
    if not file.endswith("csv"):
        raise ValueError("The file must have a .csv extension.")

    data = pd.read_csv(file, header=0)
    return data
