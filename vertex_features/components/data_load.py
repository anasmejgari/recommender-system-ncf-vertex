"""Veretex AI Pipeline."""

from kfp.dsl import component, Dataset, Input, Output


@component(base_image="python:3.12", packages_to_install=["pandas", "fsspec", "gcsfs"])
def load_dataset(
    blob_ratings: str,
    blob_movies: str,
    bucket_name: str,
    output_movie_dataset: Output[Dataset],
    output_ratings_dataset: Output[Dataset],
) -> None:
    import pandas as pd

    bucket_uri = f"gs://{bucket_name}/"

    ratings_uri = bucket_uri + blob_ratings
    ratings = pd.read_csv(ratings_uri)
    ratings.to_csv(output_ratings_dataset.path, index=False)

    movies_uri = bucket_uri + blob_movies
    movies = pd.read_csv(movies_uri)
    movies.to_csv(output_movie_dataset.path)
