"""Veretex AI Pipeline."""

from typing import NamedTuple
from kfp.dsl import component, Dataset, Input, Output

from .config import BASE_IMAGE_REC_SYS


class OutputStats(NamedTuple):
    number_of_movies: int
    number_of_users: int


@component(
    base_image=BASE_IMAGE_REC_SYS,
    packages_to_install=["pandas", "numpy", "fsspec", "gcsfs"],
)
def preprocess(
    input_movies_dataset: Input[Dataset],
    input_ratings_dataset: Input[Dataset],
    train_ratings_dataset: Output[Dataset],
    test_ratings_dataset: Output[Dataset],
) -> NamedTuple("Output", [("number_of_movies", int), ("number_of_users", int)]):
    import numpy as np
    import pandas as pd
    from rec_sys.model.train import split_dataset

    movies = pd.read_csv(input_movies_dataset.path)
    ratings = pd.read_csv(input_ratings_dataset.path)

    dict_mapping_movies = {
        movie: idx for idx, movie in enumerate(movies["movieId"].unique())
    }
    dict_mapping_users = {
        user: idx for idx, user in enumerate(ratings["userId"].unique())
    }

    movies["movieId"] = movies["movieId"].map(dict_mapping_movies)
    ratings["movieId"] = ratings["movieId"].map(dict_mapping_movies)
    ratings["userId"] = ratings["userId"].map(dict_mapping_users)
    ratings["rating"] = ratings["rating"].astype(np.int8)
    ratings = ratings.drop("timestamp", axis=1)

    n_movies = movies["movieId"].nunique()
    n_users = ratings["userId"].nunique()

    train_data, test_data = split_dataset(ratings=ratings)
    train_data.to_csv(train_ratings_dataset.path, index=False)
    test_data.to_csv(test_ratings_dataset.path, index=False)

    return n_movies, n_users
