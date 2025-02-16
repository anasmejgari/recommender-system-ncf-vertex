"""Module for the NCF Recommender System."""

import torch
import torch.nn as nn
from torch import Tensor


class NCFRecommender(nn.Module):
    """Class for the Neural Collaborative Recommender."""

    def __init__(
        self,
        num_users: int,
        num_items: int,
        embedding_dim,
        hidden_layers_size: list[int] | None = None,
    ) -> None:
        """Initialize of the class.

        Args:
            num_users (int): The number of users in the datasets
            num_items (int): The number of items in the datasets
            embedding_dim (_type_): The dimension of embeddings.
            hidden_layers_size (list[int] | None): list of hidden layers in MLP part.
        """
        super().__init__()

        self.num_users = num_users
        self.num_items = num_items
        self.embedding_dim = embedding_dim
        if hidden_layers_size:
            self.hidden_layers_size = hidden_layers_size
        else:
            self.hidden_layers_size = [64, 32, 8]

        # Embeddings
        self.user_embedding = nn.Embedding(self.num_users, self.embedding_dim)
        self.item_embedding = nn.Embedding(self.num_items, self.embedding_dim)

        # MLP Layers
        mlp_layers: list[nn.Module] = []
        input_size = self.embedding_dim * 2
        for layer_size in self.hidden_layers_size:
            mlp_layers.append(
                nn.Linear(in_features=input_size, out_features=layer_size)
            )
            mlp_layers.append(nn.ReLU())
            input_size = layer_size

        self.mlp_layers = nn.Sequential(*mlp_layers)

        # Output Layer
        final_layer_input_size = self.hidden_layers_size[-1] + self.embedding_dim
        self.output_layer = nn.Linear(
            in_features=final_layer_input_size, out_features=1
        )

    def forward(self, user_indices: Tensor, item_indices: Tensor) -> Tensor:
        """Execute a forward pass of the model.

        Args:
            user_indices (Tensor): Tensor of user's indices.
            item_indices (Tensor): Tensor of item's indices

        Returns:
            Tensor: The resulting tensor.
        """
        user_embeddings = self.user_embedding(user_indices)
        item_embeddings = self.item_embedding(item_indices)

        # GMF Dot Product
        gmf_layer = torch.mul(user_embeddings, item_embeddings)

        # MLP Side
        mlp_input = torch.cat([user_embeddings, item_embeddings], dim=1)
        mlp_output = self.mlp_layers(mlp_input)

        # Combining MLP & GMF
        final_output: Tensor = torch.cat([gmf_layer, mlp_output], dim=1)
        final_output = self.output_layer(final_output)

        output: Tensor = final_output.squeeze()
        return output
