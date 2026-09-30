# EDGAR-lxml-elt

[![Data source: SEC EDGAR](https://img.shields.io/badge/data%20source-SEC%20EDGAR-003366)](https://www.sec.gov/edgar/search/)
[![Python 3.13](https://img.shields.io/badge/python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![edgartools](https://img.shields.io/badge/built%20with-edgartools-2a78d6)](https://github.com/dgunning/edgartools)

This is going to be an end-to-end SEC filing monitor system to create investment advice.

![Annual revenue and net margin for Apple, Alphabet, Tesla, NVIDIA, BlackRock and Oracle, from XBRL financials](assets/revenue-and-net-margin.jpg)

## Data source

All data comes from the U.S. Securities and Exchange Commission's
[EDGAR](https://www.sec.gov/edgar/search/) system: Form 4 insider trades, 8-K events, 10-K XBRL financials,
13F-HR institutional holdings and Form D private offerings. Requests follow the SEC's
[fair access policy](https://www.sec.gov/os/accessing-edgar-data) (declared User-Agent, at most 10 requests/second).
