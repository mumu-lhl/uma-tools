#!/bin/python3

import argparse

import os


def main():
    parser = argparse.ArgumentParser(description="Pack source code into a zip file.")
    parser.add_argument("version", type=str)

    args = parser.parse_args()
    
    os.system(f"zip -r uma-tools-v{args.version}.zip config/ operators/ ui/ __init__.py -x **/__pycache__/* -x **/__pycache__/")

if __name__ == "__main__":
    main()
