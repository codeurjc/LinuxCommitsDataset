# Dataset of Linux Commits

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10278756.svg)](https://doi.org/10.5281/zenodo.10278756)

This is the reproduction package for the paper "A dataset of Linux Kernel commits", submitted to the Data and Tools Showcase track of the International Conference on Mining Software Repositories 2024.

## How it was obtained:

```commandline
git clone git://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
python3 -m venv venv
source venv/bin/activate
pip install perceval
nohup perceval git linux --json-line -o linux-commits-2023-11-12.json 2> linux-commits-2023-11-12-perceval.txt
tar cvzf linux-2023-11-12.tar.gz linux
```

## Contents:

*  `notebooks` : Directory with Jupyter Python notebooks showing the analysis of the dataset, including data and figures presented in the paper.

* `notebooks/links.csv` : File, in CSV format, with the list of data obtained thanks to the 'Fixes' field in commit messages. It includes columnos for the hash of the bug fixing commit (BFC) including the `Fixes` field, for the hash of the corresponding bug introducing commit (BIC), for the first line of their commit messages, and for the distance between both in number of day, and in number of commits.

* `dockerfiles` : Directory with Docker configuration to produce a container to run the notebooks.

* `commands/linux-commits-2023-11-12-perceval.txt`: Output of the Perceval command used to obtain the list of JSON documents (one per line) corresponding to the commits in the Linux kernel.


## Dataset in Zenodo

Link to Zenodo: https://doi.org/10.5281/zenodo.10278756

The Zenodo dataset includes:

* `linux-2023-11-12.tar.gz` : Compressed directory (using tar) of the linux git repository which was used to obtain commit information with Perceval.

* `linux-commits-2023-11-12.json.gz` : Commits file, as produced by Percecal, with one JSON document per line, each one corresponding to one commit.