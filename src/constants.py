import os

DOWNLOADS_FOLDER = os.environ.get("PIPELINE_DATA_DIR", "data/raw")
REPORTS_DIR = os.environ.get("REPORTS_DIR", "reports")

DATASETS_URLS = [
    "https://data.gov.ua/dataset/ed0ba0f7-f23a-4db4-8b0e-2bdef0b16eeb",

]

# CKAN API base URL for data.gov.ua
CKAN_API_URL = "https://data.gov.ua/api/3/action"
