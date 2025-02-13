import pandas as pd
import torch
from torch.utils.data import Dataset


class RatingDataset(Dataset):
    """Custom Dataset for NeuMF Training"""

    def __init__(self, ratings_df: pd.DataFrame) -> None:
        self.users = torch.LongTensor(ratings_df["userId"].values)  # Convert to tensor
        self.movies = torch.LongTensor(ratings_df["movieId"].values)
        self.ratings = torch.FloatTensor(ratings_df["rating"].values)

    def __len__(self) -> int:
        return len(self.ratings)

    def __getitem__(self, idx) -> tuple[int, int, float]:
        return (self.users[idx], self.movies[idx], self.ratings[idx])
