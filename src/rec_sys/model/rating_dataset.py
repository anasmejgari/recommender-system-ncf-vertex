"""Module for the Rating datasets."""

import pandas as pd
import torch
from torch import Tensor
from torch.utils.data import Dataset


class RatingDataset(Dataset):
    """Custom Dataset for NeuMF Training."""

    def __init__(self, ratings_df: pd.DataFrame) -> None:
        """Class initiazer.

        Args:
            ratings_df (pd.DataFrame): The dataframe of ratings.
        """
        self.users = torch.LongTensor(ratings_df["userId"].values)
        self.movies = torch.LongTensor(ratings_df["movieId"].values)
        self.ratings = torch.FloatTensor(ratings_df["rating"].values)

    def __len__(self) -> int:
        """Calculate the lenth of ratings (User-Item relationship)."""
        return len(self.ratings)

    def __getitem__(self, idx: int) -> tuple[Tensor, Tensor, Tensor]:
        """Get one item by index.

        Args:
            idx (int): The index to retrieve.

        Returns:
            tuple[Tensor, Tensor, Tensor]: tensors with ids and rating.
        """
        return (self.users[idx], self.movies[idx], self.ratings[idx])
