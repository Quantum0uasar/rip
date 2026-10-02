from ingest.downloader import download_file

# ST37 URL (you'll need to get the actual URL from the AER site)
st37_url = "https://www.aer.ca/providing-information-and-services/data-and-reports/statistical-reports/st37"

# Download it
filepath, checksum = download_file(st37_url, "st37")
print(f"Downloaded to: {filepath}")
print(f"Checksum: {checksum}")
