\# Real refXAS — KIT VM Deployment Checklist



\## Current Repository



Repository:



https://github.com/pathireddysivasaikumar/Real-RefXAS



This repository contains the current Real refXAS working version, based on the protected StateJun structure with selected V5 improvements.



\---



\## Current Working Features



The following local workflow has been tested successfully:



1\. Upload XAS data file

2\. Verify extracted metadata

3\. Submit dataset to SciCat

4\. Store metadata in MongoDB

5\. Store application data in PostgreSQL

6\. Review dataset in curator page

7\. View quality-control graph

8\. Approve dataset

9\. Show approved dataset in public dataset list

10\. Open public dataset detail page



\---



\## Supported Upload Formats



Current upload page accepts:



\- `.xdi`

\- `.dat`

\- `.spec`

\- `.txt`

\- `.csv`

\- `.h5`

\- `.hdf`

\- `.hdf5`

\- `.nxs`

\- `.nexus`



\---



\## Important Local Improvements



This version includes:



\- Improved Real refXAS upload workflow

\- Improved quality-control plot display

\- Element and edge auto-detection from filename/header

\- Cleaner supported-format message on upload page

\- Curator review and approval workflow

\- Public dataset visibility after curator approval

\- Docker-based SciCat, MongoDB, PostgreSQL and Django deployment

\- Local Windows-compatible MongoDB Docker volume setup



\---



\## Secrets and Private Config Files



The following files are intentionally not committed to GitHub:



\- `xafsdb\_deployment/.env`

\- `xafsdb\_deployment/config/backend/config.env`

\- `xafsdb\_deployment/config/backend/functionalAccounts.json`

\- `xafsdb\_deployment/config/xafsdb/\_auth\_constants.py`

\- `xafsdb\_deployment/temp/`

\- local backup files

\- local patch scripts



Use:



```bash

xafsdb\_deployment/.env.example

