"""
 A script to read a csv with data points and increases the number of points by interpolating and outputs a Zinc file.
"""
import argparse

from csv_to_exelem.csv_to_exelem import CsvToExf

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description='Convert a csv file to an exnode file.')
    ap.add_argument('-i', '--input', help='Input csv file', required=True)
    args = ap.parse_args()

    inputFile = args.input
    nodeOffset = 1
    elementOffset = 1

    CsvToExf(inputFile, nodeOffset, elementOffset)