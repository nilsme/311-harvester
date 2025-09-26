# README

This project provides a command-line utility for downloading the full NYC 311
service request dataset (dataset id `erm2-nwe9`) from the
[NYC OpenData](https://opendata.cityofnewyork.us/) Portal using the official
bulk CSV export endpoint.

Bulk download requires an ``App-Token`` that can be created after a
registration. See the
[API Dokumentation](https://dev.socrata.com/foundry/data.cityofnewyork.us/erm2-nwe9)
for further details.

> Download size is around 24 GB (as of 09/26/2025) with 41.1 million rows and
> 41 columns.

Links

- [Data description](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9)
- [Data dictionary](https://data.cityofnewyork.us/api/views/erm2-nwe9/files/b372b884-f86a-453b-ba16-1fe06ce9d212?download=true&filename=311_ServiceRequest_2010-Present_DataDictionary_Updated_2023.xlsx)
- [API documentation](https://dev.socrata.com/foundry/data.cityofnewyork.us/erm2-nwe9)

## Quickstart

```bash
python download_all.py --verbose
```

## Development

### Code Quality and Security

Install needed packages for code formatting

```bash
pip install -r requirements.txt
```

Set up pre-commit

```bash
pre-commit install
```

Run pre-commit for tests

```bash
pre-commit run --all-files
```

Bypass all hooks for a commit

```bash
git commit --no-verify -m "Commit message"
```

### Documentation

Deploy Docs to Github Pages

```bash
mkdocs gh-deploy
```
