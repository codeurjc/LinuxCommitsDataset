#!/usr/bin/python3

import argparse
import json
import gzip
import random

# Parse command line arguments
parser = argparse.ArgumentParser(
    description = "Get a random sample of commits from a Perceval on-line JSON list of commits"
    )
parser.add_argument("-i", "--input",
                    help = "File with JSONs created by perceval. Can be a gziped file")
parser.add_argument("-y", "--year",
                    help = "Year of the commits to choose from")
parser.add_argument("-n", "--number",
                    help = "Number of commits to choose")
parser.add_argument("-s", "--seed",
                    help = "Seed integer, for reproducibility")
args = parser.parse_args()

commitsList = []

if args.input.endswith('gz'):
    func = gzip.open
elif args.input.endswith('json'):
    func = open

with func(args.input) as inputfile:
    for line in inputfile:
        commit = json.loads(line)
        year = commit['data']['CommitDate'].split()[4] # Get year of commit
        if year == args.year:
            commitsList.append(commit['data']['commit'])

random.seed(args.seed)
chosen = random.sample(commitsList, int(args.number))
print('\n'.join(chosen))
