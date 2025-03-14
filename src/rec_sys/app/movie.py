"""Module to modelize a movie."""

from pydantic import BaseModel, field_validator

from rec_sys.app.constants import STRING_NO_GENRE


class Movie(BaseModel):
    """Pydatic Subclass for a movie representatin."""

    imdb_id: int
    title: str
    year: int
    cover: str
    genres: str

    @field_validator("year")
    @classmethod
    def validate_year(cls, value: int) -> int:
        """Validate if the year is formatted correctly.

        Args:
            value (int): the year passed by the user.

        Raises:
            ValueError: The year is not valid

        Returns:
            int: year
        """
        if value < 1900:
            raise ValueError(f"Year {value} is not valid.")
        return value

    @field_validator("genres")
    @classmethod
    def validate_genres(cls, genres: str) -> str:
        """Format genres of a movie.

        Args:
            genres (str): List of non formatted genres.

        Returns:
            str: Formatted genres.
        """
        list_genres = genres.split("|")
        if STRING_NO_GENRE in list_genres:
            list_genres.remove(STRING_NO_GENRE)

        genres_to_return = ", ".join(list_genres)
        return genres_to_return
