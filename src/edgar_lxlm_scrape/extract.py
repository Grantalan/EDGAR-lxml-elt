"""Download raw data from SEC EDGAR and save it to RustFS, untouched."""

import os
import time
from datetime import date

import boto3
import requests
from dotenv import load_dotenv

load_dotenv()

# SEC blocks requests that don't say who you are ("Name email").
HEADERS = {"User-Agent": os.getenv("SEC_USER_AGENT")}

BUCKET = os.getenv("S3_BUCKET")
s3 = boto3.client(
    "s3",
    endpoint_url=os.getenv("S3_ENDPOINT_URL"),
    aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
    region_name="us-east-1",
)

# SEC's insider trading data sets start in 2006.
FIRST_YEAR = 2006


def fetch(url):
    """Download a URL from SEC and return the raw bytes."""
    time.sleep(0.2)  # stay well under SEC's limit of 10 requests per second
    resp = requests.get(url, headers=HEADERS, timeout=120)
    resp.raise_for_status()
    return resp.content


def land(key, data):
    """Save raw bytes to RustFS exactly as they arrived."""
    s3.put_object(Bucket=BUCKET, Key=key, Body=data)
    print(f"landed s3://{BUCKET}/{key} ({len(data):,} bytes)")


def already_landed(key):
    """True if this file is already in RustFS."""
    found = s3.list_objects_v2(Bucket=BUCKET, Prefix=key)
    return found["KeyCount"] > 0


def make_bucket():
    """Create the bucket the first time we run."""
    names = [b["Name"] for b in s3.list_buckets()["Buckets"]]
    if BUCKET not in names:
        s3.create_bucket(Bucket=BUCKET)


def get_insider_trades(year, quarter):
    """Every Form 3/4/5 insider trade filed in one quarter, as one zip file."""
    name = f"{year}q{quarter}_form345.zip"
    key = f"insider_trades/{name}"
    if already_landed(key):
        print(f"skip {key} (already landed)")
        return
    url = f"https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/{name}"
    land(key, fetch(url))


def get_all_insider_trades():
    """Every quarter from 2006 until now. Quarters SEC hasn't published yet are skipped."""
    for year in range(FIRST_YEAR, date.today().year + 1):
        for quarter in [1, 2, 3, 4]:
            try:
                get_insider_trades(year, quarter)
            except requests.HTTPError:
                print(f"skip {year}q{quarter} (not published yet)")


def get_company_tickers():
    """Every ticker SEC knows about, with CIK, company name and exchange."""
    data = fetch("https://www.sec.gov/files/company_tickers_exchange.json")
    land(f"company_tickers/{date.today()}.json", data)


def get_filings(cik, ticker):
    """A company's filing history (10-K, 10-Q, 8-K, Form 4, ...)."""
    url = f"https://data.sec.gov/submissions/CIK{cik:010d}.json"
    land(f"filings/{ticker}/{date.today()}.json", fetch(url))


if __name__ == "__main__":
    make_bucket()
    get_company_tickers()
    get_all_insider_trades()
