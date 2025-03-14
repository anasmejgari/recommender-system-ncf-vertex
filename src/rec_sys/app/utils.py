"""Module for utils of front-end."""

from functools import cache

from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value

from rec_sys.app.constants import (
    DEFAULT_IMAGE,
    ENDPOINT_ID,
    FILM_NAME_AND_YEAR_REGEX,
    IMDB_ACCES,
    IMDB_DATA,
    LOCAION,
    MOVIES,
    PROJECT_ID,
)
from rec_sys.app.movie import Movie


@cache
def get_recommended_movies(id_user: int) -> list[Movie]:
    """Recommend movies for a user.

    Args:
        id_user (int): User ID.

    Returns:
        list[Movie]: list of recommended movies.
    """
    list_of_ids = get_recommended_movies_ids(id_user=id_user)
    list_of_movies = []
    for id_movie in list_of_ids:
        movie = movie_from_id(id_movie=id_movie)
        list_of_movies.append(movie)
    return list_of_movies


def movie_from_id(id_movie: int) -> Movie:
    """Generate movie content from its id.

    Args:
        id_movie (int): The ID of the movie.

    Returns:
        Movie: The movie object linked to the id
    """
    movie_details = MOVIES.loc[MOVIES["movieId"] == id_movie].iloc[0]
    movie_representaion = movie_details["title"]
    title, year = extract_movie_name_and_year(movie_representaion)

    imdb_movie_data = IMDB_DATA.loc[IMDB_DATA["movieId"] == id_movie, ["imdbId"]]
    imdb_movie_id = imdb_movie_data.iloc[0]["imdbId"]
    cover = get_movie_cover(imdb_movie_id=imdb_movie_id)

    return Movie(
        imdb_id=imdb_movie_id,
        title=title,
        cover=cover,
        year=year,
        genres=movie_details["genres"],
    )


def get_movie_cover(imdb_movie_id: int) -> str:
    """Search for a movie's cover.

    Args:
        imdb_movie_id (int): The IMDB movie's ID

    Returns:
        str: URL of the cover
    """
    movie = IMDB_ACCES.get_movie(imdb_movie_id)
    if "cover url" in movie:
        return movie["cover url"]
    else:
        return DEFAULT_IMAGE


def extract_movie_name_and_year(movie_representation) -> tuple[str, int]:
    """Extract movie title and year of production from string representation.

    Args:
        movie_representation (string): String representation of type 'name (year)'

    Raises:
        ValueError: Error while applying REGEX

    Returns:
        tuple[str, int]: the movie title and the year of production.
    """
    search_in_regex = FILM_NAME_AND_YEAR_REGEX.search(movie_representation)
    if search_in_regex:
        title = search_in_regex.group(1).strip()
        year = search_in_regex.group(2)
        if year and title:
            return title, int(year)

    raise ValueError(
        f"Error while extracting the title and movie's name from {movie_representation}"
    )


def get_recommended_movies_ids(id_user: int) -> list[int]:
    """Call the Vertex AI Endpoint to get recommendations.

    Args:
        id_user (int): Id of the user.

    Returns:
        list[int]: List of recommended movies ids
    """
    instances = [{"id": id_user}]
    api_endpoint = "europe-west2-aiplatform.googleapis.com"
    client_options = {"api_endpoint": api_endpoint}
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)

    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests
    instances = [
        json_format.ParseDict(instance_dict, Value()) for instance_dict in instances
    ]
    parameters_dict = {}  # type: ignore
    parameters = json_format.ParseDict(parameters_dict, Value())

    endpoint = client.endpoint_path(
        project=str(PROJECT_ID), location=str(LOCAION), endpoint=str(ENDPOINT_ID)
    )
    response = client.predict(
        endpoint=endpoint, instances=instances, parameters=parameters, timeout=90
    )

    return response
