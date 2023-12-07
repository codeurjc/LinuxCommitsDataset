# Dataset of Linux Commits

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10287486.svg)](https://doi.org/10.5281/zenodo.10287486)

This is the reproduction package for the paper "A dataset of Linux Kernel commits", submitted to the Data and Tools Showcase track of the International Conference on Mining Software Repositories 2024.

The dataset consists of 3 files hosted on [Zenodo](https://doi.org/10.5281/zenodo.10287486):
* `linux-2023-11-12.tar.gz` : Compressed directory (using tar) of the linux git repository which was used to obtain commit information with Perceval.
* `linux-commits-2023-11-12.json.gz` : Commits file, as produced by Percecal, with one JSON document per line, each one corresponding to one commit.
- `bfc_bic.csv`: List with all Bug-Fixing Commits (BFC) and Bug-Introducing Commits (BIC) pairs (links) obtained from the previous artifact.
- `LinuxCommitsDataset.zip`: This repository, with all the scripts and notebooks needed to reproduce the dataset.

Below is detailed how them were obtained:

## Obtaining the Linux Kernel repository and commit list:

The following are the commands performed to obtain the list of Linux Kernel commits using the Python Perceval library. As a result, the file `linux-commits-2023-11-12.json` is obtained, besides saving the Linux Kernel repository in a tar.gz (`linux-2023-11-12.tar.gz`).

```commandline
git clone git://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
python3 -m venv venv
source venv/bin/activate
pip install perceval
nohup perceval git linux --json-line -o linux-commits-2023-11-12.json 2> linux-commits-2023-11-12-perceval.txt
tar cvzf linux-2023-11-12.tar.gz linux
```

## Contents of the reproduction package:

*  `notebooks` : Directory with Jupyter Python notebooks showing the analysis of the dataset, including data and figures presented in the paper.
    * `GeneralAnalysis.ipynb`:
        * **Prerequisite**: You must have generated the file `linux-commits-2023-11-12.json` and placed it in the root of the reproduction package.
        * Provides an analysis of the commit dataset.
    * `GenerateBFC-BIC_Dayaset.ipynb`:
        * **Prerequisite**: You must have generated the file `linux-commits-2023-11-12.json` and placed it in the root of the reproduction package. Also, if you want to calculate the distance in commits, the Linux repository (`linux-2023-11-12.tar.gz`) unzipped in the `notebooks/` folder.
        * Generate BFC-BIC dataset (`bfc_bic.csv`)
    * `BFC-BIC_LinksAnalysis.ipynb`:
        * **Prerequisite**: You must have generated the file `linux-commits-2023-11-12.json` and placed it in the root of the reproduction package and the file `bfc_bic.csv` in `notebooks/` folder.
        * Provides an analysis of the BFC-BIC dataset dataset.    

* `notebooks/bfc_bic.csv` : File, in CSV format, with the list of data obtained thanks to the 'Fixes' field in commit messages. It includes columnos for the hash of the bug fixing commit (BFC) including the `Fixes` field, for the hash of the corresponding bug introducing commit (BIC), for the first line of their commit messages, and for the distance between both in number of day, and in number of commits.
**Note:** *This is the same file uploaded to Zenodo, stored for convenience for use with notebooks.*

* `dockerfiles` : Directory with Docker configuration to produce a container to run the notebooks.

* `commands/linux-commits-2023-11-12-perceval.txt`: Output of the Perceval command used to obtain the list of JSON documents (one per line) corresponding to the commits in the Linux kernel.