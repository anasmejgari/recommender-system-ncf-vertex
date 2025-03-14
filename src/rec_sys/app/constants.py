"""Constants to use for the frontend."""

import os
import re
from pathlib import Path

import imdb
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


ENDPOINT_ID = os.getenv("ENDPOINT_ID")
PROJECT_ID = os.getenv("PROJECT_ID")
LOCAION = os.getenv("REGION")

# get a movie
DATA_DIR = Path(__file__).parent.parent / "data"

MOVIES_DATA_PATH = Path(DATA_DIR) / "movies.csv"
IMDB_DATA_PATH = Path(DATA_DIR) / "links.csv"


MOVIES = pd.read_csv(MOVIES_DATA_PATH)
IMDB_DATA = pd.read_csv(IMDB_DATA_PATH)

DEFAULT_IMAGE = "https://as2.ftcdn.net/jpg/03/45/99/01/1000_F_345990153_Dx8FtImSpV72Dlea6deFqf1QfJJ6ggqj.jpg"
FILM_NAME_AND_YEAR_REGEX = re.compile(r"^(.*)\s\((\d{4})\)$")
STRING_NO_GENRE = "(no genres listed)"

IMDB_ACCES = imdb.IMDb()
