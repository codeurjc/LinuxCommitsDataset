#! /usr/bin/env python3

import csv
from datetime import datetime
import enum
import gzip
import json
import re
import sys

commits_filename = 'linux-commits-2023-11-12.json.gz'

class Fixes_Kind(enum.Enum):
    NO_MESSAGE = 0
    PERFECT = 1
    NOFIXES = 2
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
    if "Fixes" not in message:
        # Nothing to do, no fixes
        return None, Fixes_Kind.NOFIXES
    # Search: "Fixes: <hash>"
    message_simple = message.replace('"','').replace('(',' ').replace(')',' ')
    match = re.search(r"Fixes:[^\S\n]+(\b[0-9a-f]{5,40}\b)", message_simple)
    if match is not None:
        bic_hash = match.group(1)
        return bic_hash, Fixes_Kind.PERFECT
    else:
        return None, Fixes_Kind.OTHER

def find_path(commits_dict, start, end):
    parents_set = set(commits_dict[start]['parents'])
    checked_set = set()
    max_parents = len(parents_set)
    max_parents_later = len(parents_set)
    end_date = commits_dict[end]['date']
    lenght = 0
    found = False
    while not found and (len(parents_set) > 0):
        lenght += 1
        if end in parents_set:
            found = True
        else:
            parents_lists = [commits_dict[hash]['parents'] for hash in parents_set]
            parents = [hash for parents_list in parents_lists
                       for hash in parents_list]
            parents_set = set(parents) - checked_set
            checked_set.update(parents_set)
            if len(parents_set) > max_parents:
                max_parents = len(parents_set)
            for parent in list(parents_set):
                if commits_dict[parent]['date'] < end_date:
                    parents_set.remove(parent)
            if len(parents_set) > max_parents_later:
                max_parents_later = len(parents_set)
    print(f"{found} {lenght:<6} {max_parents:<6} {max_parents_later:6}")
    if found:
        return lenght
    else:
        return None


def read_commits(filename):
    """Produce commits_dict by reading filename.

    filename is in JSON format, maybe gzipped.
    """

    date_format = "%a %b %d %H:%M:%S %Y %z"
    # Commits dictionary
    commits = {}
    # Commits with short (<10) hash
    short_counter = 0
    # Fixes line with short (<10) hash
    short_fixes_counter = 0
    # Message with no newline
    nonl_counter = 0
    counter = 0

    for commit in get_commits(commits_filename):
        if counter > 11445000:
            break
        counter = counter + 1
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
            'date': datetime.strptime(commit['data']['CommitDate'], date_format),
            'parents': [parent[:10] for parent in commit['data']['parents']]
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

def annotate_fixes(commits_dict):
    """Annotate commits_dict with stats for fixes

    In commits with a fixes line, annotate with date of fixes,
    time since fixes, number of commits since fixes."""

    # Number of commits with no fixes line
    nofixes = 0
    # Number of too short fixes hashes
    tooshort = 0
    # Number of fixes hashes not found in previous commits
    notfound = 0
    # Number of good fixes
    good = 0
    # Number of fixes for which no path to fixes commit was found
    nopath = 0

    # Find if fixes are in commits_dict (maybe with a shorter lenght)
    for commit in commits_dict.values():
        if 'fixes' not in commit:
            # No fixes line, nothing to do here
            nofixes += 1
            continue
        if len(commit['fixes']) < short_lengths[-1]:
            # Previous commit hash is too short to try to find it
            print(f"Too short hash for a fix commit: {commit['fixes']}", file=sys.stderr)
            tooshort += 1
            continue
        short_commits_len_dict = short_commits_dict[len(commit['fixes'])]
        if commit['fixes'] not in short_commits_len_dict:
            # Fixes commit cannot be found, nothing to do here
            notfound += 1
            continue
        good += 1

        # Find number of commits to the fixes commit
        fixes_hash = short_commits_len_dict[commit['fixes']]['hash']
        print(f"{good:>6}", fixes_hash, end=' ')
        commit['fixes_hash'] = fixes_hash
        fixes_date = short_commits_len_dict[commit['fixes']]['date']
        sys.setrecursionlimit(100000)
        path_length = find_path(commits_dict,
                                commit['hash'], fixes_hash)
        commit['fixes_commits'] = path_length

        fixes_time = commit['date'] - fixes_date
        commit['fixes_date'] = fixes_date
        commit['fixes_time'] = round(fixes_time.total_seconds())
        if path_length is None:
            nopath += 1

    return nofixes, tooshort, notfound, nopath

if __name__ == '__main__':
    # Now, run the show
    commits_dict = {}
    short_commits_dict = {}
    fixes_counter = {kind: 0 for kind in Fixes_Kind}

    commits_dict, short_counter, short_fixes_counter, nonl_counter = read_commits(commits_filename)

    # Produce short_commits_dict, to more easily check for fixes commits
    short_lengths = [9, 8, 7, 6, 5]
    short_commits_dict[10] = commits_dict
    for short_length in short_lengths:
        length_commits_dict = {}
        for hash, commit in commits_dict.items():
            length_commits_dict[hash[:short_length]] = commit
        short_commits_dict[short_length] = length_commits_dict

    print("** All commits read, fixes found")
    print(f"   Commits with no message: {fixes_counter[Fixes_Kind.NO_MESSAGE]}")
    print(f"   Commits with no 'Fixes' string: {fixes_counter[Fixes_Kind.NOFIXES]}")
    print(f"   Commits with perfect fixes lines: {fixes_counter[Fixes_Kind.PERFECT]}")
    print(f"   Other cases: {fixes_counter[Fixes_Kind.OTHER]}")

    print(f"   Commits in original dataset with short (<10) hash: {short_counter}")
    print(f"   Commits in original dataset with no new line in message: {nonl_counter}")
    print(f"   Fixed lines with short (<10) hash: {short_fixes_counter}")

    nofixes, tooshort, notfound, nopath = annotate_fixes(commits_dict)

    print("** All commits annotated with fixes information")
    print(f"   Commits with no fixes line: {nofixes}")
    print(f"   Fixes hashes too short: {tooshort}")
    print(f"   Fixes hashes not found in previous commits: {notfound}")
    print(f"   Fixes hashes to which no path was found: {nopath}")

    csv_headers = ['hash', 'date', 'fixes_hash', 'fixes_date', 'fixes_commits', 'fixes_time']
    with open("fixes.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
        writer.writeheader()
        for commit in commits_dict.values():
            row = {}
            for field in csv_headers:
                row[field] = commit.get(field, None)
            writer.writerow(row)
