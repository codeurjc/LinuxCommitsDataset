#! /usr/bin/env python3

import enum
import gzip
import json
import re

commits_filename = 'linux-commits-2023-11-12.json.gz'

class Fixes_Kind(enum.Enum):
    NO_MESSAGE = 0
    PERFECT = 1
    OTHER = 10

def get_commits(filename):
    """Load commits from file, as an iterator"""

    if filename.endswith('.gz'):
        open_fn = gzip.open
    else:
        open_fn = open

    with open_fn(filename) as f:
        for commit in f:
            yield json.loads(commit)

def get_fixes_hash(message):
    # Search: "Fixes: <hash>"
    match = re.search(r"Fixes:[^\S\n]+(\b[0-9a-f]{5,40}\b)", message)
    if match is not None:
        bic_hash = match.group(1)
        return bic_hash, Fixes_Kind.PERFECT
    else:
        return None, Fixes_Kind.OTHER
#        bic_hash = analyzeCornerCases(commit)
#        if bic_hash is None: return None
#        corner_cases += 1

def find_path(graph, start, end, path=[]):
    """Find the path of start commit, parent after parent, to end commit"""
    path = path + [start]
    if start == end:
        return path
    if start in graph.keys():
        return None
    for parent in getParents(start):
        if parent not in path:
            newpath = find_path(graph, parent, end, path)
            if newpath is not None: return newpath
        return None
def getParents(_hash):
    return all_commits_map[_hash[0:12]][0]['data']['parents']

def commitDistance(bfc_hash, bic_hash):
    return len(find_path(all_commits_map, bfc_hash, bic_hash))-1




# Now, run the show
commits_dict = {}
short_commits_dict = {}
fixes_counter = {kind: 0 for kind in Fixes_Kind}
# Counter for fixed hashes not found in previous commits
fixed_not_found_counter = 0

def read_commits(filename):
    """Produce commits_dict by reading filename.

    filename is in JSON format, maybe gzipped.
    """

    # Commits dictionary
    commits = {}
    # Commits with short (<10) hash
    short_counter = 0
    # Fixes line with short (<10) hash
    short_fixes_counter = 0
    # Message with no newline
    nonl_counter = 0
    #for i, commit in enumerate(get_commits(commits_filename)):
    for commit in get_commits(commits_filename):
        hash = commit['data']['commit'][:10]
        try:
            message = commit['data']['message']
            fixes_hash, kind = get_fixes_hash(message)
        except KeyError:
            fixes_hash, kind = None, Fixes_Kind.NO_MESSAGE
            message = ""

        if len(hash) < 10:
            short_counter += 1
        data = {
            'hash': hash,
            'date': commit['data']['CommitDate'],
            'parents': commit['data']['parents']
        }
        try:
            header = message[:message.index('\n')]
        except ValueError:
            nonl_counter += 1
            header = message
        data['header'] = header

        if fixes_hash is not None:
            data['fixes'] = fixes_hash[:10]
            if len(data['fixes']) < 10:
                short_fixes_counter += 1
        fixes_counter[kind] += 1
        commits[hash] = data
    return commits, short_counter, short_fixes_counter, nonl_counter

commits_dict, short_counter, short_fixes_counter, nonl_counter = read_commits(commits_filename)

# Produce short_commits_dict
short_lengths = [9, 8, 7]
short_commits_dict[10] = commits_dict
for short_length in short_lengths:
    length_commits_dict = {}
    for hash, commit in commits_dict.items():
        length_commits_dict[hash[:short_length]] = commit
    short_commits_dict[short_length] = length_commits_dict

# Find if fixes are in commits_dict (maybe with a shorter lenght)
for commit in commits_dict.values():
    try:
        if commit['fixes'] not in short_commits_dict[len(commit['fixes'])]:
            fixed_not_found_counter += 1
    except KeyError:
        pass

print(f"No commit message: {fixes_counter[Fixes_Kind.NO_MESSAGE]}")
print(f"Perfect fixes lines: {fixes_counter[Fixes_Kind.PERFECT]}")
print(f"Other cases: {fixes_counter[Fixes_Kind.OTHER]}")
print(f"Fixed hashes not found in previous commits: {fixed_not_found_counter}")

print(f"Commits in original dataset with short (<10) hash: {short_counter}")
print(f"Commits in original dataset with no new line in message: {nonl_counter}")
print(f"Fixed lines with short (<10) hash: {short_fixes_counter}")
