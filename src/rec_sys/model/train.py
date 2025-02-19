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
    device: device,
    epochs: int = 5,
    learning_rate: float = 0.001,
) -> tuple[NCFRecommender, float]:
    """Train NCF model with MSE loss.

    Args:
        model (NCFRecommender): The model instance.
        train_loader (DataLoader): The training loader for pytorch.
        device (device): The device type (cuda or cpu)
        epochs (int): Number of training epoch. Defaults to 5.
        learning_rate (float): Optimizer's learning rate. Defaults to 0.001.

    Returns:
        tuple[NCFRecommender, float]: the model and the training RMSE.
    """
    optimizer = Adam(model.parameters(), lr=learning_rate)
    loss_fn = nn.MSELoss()

    for epoch in range(1, epochs + 1):
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

        training_rmse = torch.sqrt(total_train_loss / len(train_loader))

        print(f"Epoch {epoch}/{epochs}: RMSE = {training_rmse:.4f}.")

    return model, training_rmse


def eval_model(model: NCFRecommender, ratings_test: pd.DataFrame) -> float:
    """Evaluate a model.

    Args:
        model (NCFRecommender): The model to evaluate
        ratings_test (pd.DataFrame): The test set used for evaluation

    Returns:
        float: the metric evaluation
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # Load test data to DataLoader for pytorch
    test_dataset = RatingDataset(ratings_test)
    test_loader = DataLoader(test_dataset, batch_size=len(test_dataset), shuffle=True)

    model.eval()  # Set the model to evaluation mode
    loss_fn = nn.MSELoss()  # Mean Square error
    total_valid_loss = 0
    with torch.no_grad():
        for users, items, labels in test_loader:
            users, items, labels = (
                users.to(device),
                items.to(device),
                labels.to(device),
            )

            target = model(users, items)
            loss = loss_fn(target, labels)
            total_valid_loss += loss.item()

    avg_valid_loss = torch.sqrt(total_valid_loss / len(test_loader))
    print(f"RMSE for test set {avg_valid_loss}")
    return avg_valid_loss


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
    ratings_train: pd.DataFrame,
    n_users: int,
    n_movies: int,
    embedding_dim: int = 64,
    batch_size: int = 64,
    epochs: int = 5,
    learning_rate: float = 0.001,
) -> tuple[NCFRecommender, float]:
    """Load and preprocess data, and train the model.

    Args:
        ratings_train (pd.DataFrame): the ratings dataset.
        n_users (int): Overall number of users.
        n_movies (int): Overall number of movies
        embedding_dim (int): dimension of embeddings of users and movies.
        batch_size (int): Batch size used for training.
        epochs (int): Nuulber of training epochs.
        learning_rate (float): The learning rate for the optimizer.

    Returns:
        tuple[NCFRecommender, float]: the model and the training RMSE.
    """
    training_dataset = RatingDataset(ratings_train)
    train_loader = DataLoader(training_dataset, batch_size=batch_size, shuffle=True)

    # Initialize the model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = NCFRecommender(n_users, n_movies, embedding_dim).to(device)
    model, training_rmse = train_model(
        model,
        train_loader,
        device=device,
        epochs=epochs,
        learning_rate=learning_rate,
    )

    return model, training_rmse
