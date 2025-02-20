import os

from dotenv import load_dotenv

load_dotenv()

REPO_ARTIFACT = os.getenv("PYTHON_ARTIFACT_REPO_NAME")

REPO_REGION = os.getenv("REGION")

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")

BASE_IMAGE_REC_SYS = os.getenv("BASE_IMAGE_REC_SYS")
