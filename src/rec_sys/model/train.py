"""Module with function to train the model and preprocess datasets."""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch import device
from torch.optim import Adam
from torch.utils.data import DataLoader

from rec_sys.model.neural_collaborative_filtering import NCFRecommender
from rec_sys.model.rating_dataset import RatingDataset


def train_model(
    model: NCFRecommender,
    train_loader: DataLoader,
    validation_loader: DataLoader,
    device: device,
    epochs: int = 5,
    learning_rate: float = 0.001,
) -> NCFRecommender:
    """Train NCF model with MSE loss.

    Args:
        model (NCFRecommender): The model instance.
        train_loader (DataLoader): The training loader for pytorch.
        validation_loader (DataLoader): The validation loader for pytorch
        device (device): The device type (cuda or cpu)
        epochs (int): Number of training epoch. Defaults to 5.
        learning_rate (float): Optimizer's learning rate. Defaults to 0.001.

    Returns:
        NCFRecommender: The trained model.
    """
    optimizer = Adam(model.parameters(), lr=learning_rate)
    loss_fn = nn.MSELoss()

    for epoch in range(epochs):
        model.train()  # Training mode
        total_train_loss = 0
        for users, items, labels in train_loader:
            users, items, labels = users.to(device), items.to(device), labels.to(device)

            optimizer.zero_grad()  # Reset gradients
            predictions = model(users, items)
            loss = loss_fn(predictions, labels)  # Compute loss
            loss.backward()  # Backpropagation
            optimizer.step()  # Update model weights

            total_train_loss += loss.item()

        model.eval()
        total_valid_loss = 0
        with torch.no_grad():
            for users, items, labels in validation_loader:
                users, items, labels = (
                    users.to(device),
                    items.to(device),
                    labels.to(device),
                )

                target = model(users, items)
                loss = loss_fn(target, labels)
                total_valid_loss += loss.item()

        avg_train_loss = total_train_loss / len(train_loader)
        avg_valid_loss = total_valid_loss / len(validation_loader)
        print(
            f"Epoch {epoch + 1}/{epochs}, "
            f"Train Loss: {avg_train_loss:.4f}, "
            f"Validation Loss: {avg_valid_loss:.4f}"
        )

    return model


def split_dataset(
    ratings: pd.DataFrame, threshold: int = 15
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split dataset into compatible train and testing datasets.

    Args:
        ratings (pd.DataFrame): The ratings dataframe
        threshold (int, optional): number of occurence to consider.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: the training and test datasets.
    """
    # Generate stats
    ratings_stats = ratings.groupby("userId").agg({"rating": ["count"]})
    ratings_stats.columns = ["num_ratings"]

    #
    users_with_more_threshold_reviews = list(
        ratings_stats.loc[ratings_stats["num_ratings"] > threshold].index
    )

    indices_test = []
    for user_id in users_with_more_threshold_reviews:
        movie_ids = np.random.choice(
            ratings[ratings["userId"] == user_id]["movieId"].values, 5
        )
        sub_ratings_movie = ratings[
            (ratings["userId"] == user_id) & (ratings["movieId"].isin(movie_ids))
        ]

        indices_test.extend(list(sub_ratings_movie.index))

    ratings_test = ratings[indices_test]
    ratings_train = ratings.drop(indices_test)
    return ratings_train, ratings_test


def load_data_and_train(
    ratings: pd.DataFrame, movies: pd.DataFrame, batch_size: int = 64
) -> NCFRecommender:
    """Load and preprocess data, and train the model.

    Args:
        ratings (pd.DataFrame): the ratings dataset.
        movies (pd.DataFrame): movies metadata
        batch_size (int): batch size for training. Defaults to 64.

    Returns:
        NCFRecommender: The trained model.
    """
    ratings_train, ratings_test = split_dataset(ratings=ratings)
    training_dataset = RatingDataset(ratings_train)
    test_dataset = RatingDataset(ratings_test)

    # Create DataLoader
    train_loader = DataLoader(training_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=True)

    # N items & Users
    num_users = ratings["userId"].nunique()
    num_items = movies.index.nunique()
    embdedding_dim = 64

    # Initialize the model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = NCFRecommender(num_users, num_items, embdedding_dim).to(device)
    model = train_model(model, train_loader, test_loader, device)

    return model
