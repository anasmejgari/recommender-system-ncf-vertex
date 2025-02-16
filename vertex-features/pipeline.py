"""Veretex AI Pipeline."""

# import numpy as np
# import pandas as pd
# from kfp.v2.dsl import component


# @component
# def load_dataset(
#     blob_ratings: str, blob_movies: str, bucket_name: str
# ) -> tuple[pd.DataFrame, pd.DataFrame]:
#     bucket_uri = f"gs://{bucket_name}/"
#     ratings_uri = bucket_uri + blob_ratings
#     movies_uri = bucket_uri + blob_movies

#     ratings = pd.read_csv(ratings_uri)
#     movies = pd.read_csv(movies_uri)
#     return movies, ratings


# @component(base_image="python:3.12", packages_to_install=["pandas", "numpy"])
# def preprocess(
#     movies: pd.DataFrame, ratings: pd.DataFrame
# ) -> tuple[pd.DataFrame, pd.DataFrame]:
#     dict_mapping_movies = {
#         movie: idx for idx, movie in enumerate(movies["movieId"].unique())
#     }
#     dict_mapping_users = {
#         user: idx for idx, user in enumerate(ratings["userId"].unique())
#     }

#     movies["movieId"] = movies["movieId"].map(dict_mapping_movies)
#     ratings["movieId"] = ratings["movieId"].map(dict_mapping_movies)
#     ratings["userId"] = ratings["userId"].map(dict_mapping_users)

#     ratings["rating"] = ratings["rating"].astype(np.int8)
#     ratings = ratings.drop("timestamp", axis=1)
#     movies.drop(["genres"], axis=1, inplace=True)
#     movies.set_index("movieId", inplace=True)

#     return movies, ratings


# @component(base_image="python:3.12",
#            packages_to_install=["rec-sys"], pip_index_urls=[])
# def train(movies, ratings):
#     from rec_sys.model.train import load_data_and_train

#     model = load_data_and_train(ratings=ratings, movies=movies)
#     return model
