import torch.nn as nn
import torch


class NeuralCollaborativeFilteringRecommender(nn.Module):

    def __init__(
        self,
        num_users: int,
        num_items: int,
        embedding_dim: int,
        hidden_layers_size=[64, 32, 8],
    ) -> None:
        super(NeuralCollaborativeFilteringRecommender, self).__init__()

        self.num_users = num_users
        self.num_items = num_items
        self.embedding_dim = embedding_dim
        self.hidden_layers_size = hidden_layers_size

        # Embeddings
        self.user_embedding = nn.Embedding(self.num_users, self.embedding_dim)
        self.item_embedding = nn.Embedding(self.num_items, self.embedding_dim)

        # MLP Layers
        mlp_layers = []
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

    def forward(self, user_indices, item_indices):
        user_embeddings = self.user_embedding(user_indices)
        item_embeddings = self.item_embedding(item_indices)

        # GMF Dot Product
        gmf_layer = torch.mul(user_embeddings, item_embeddings)

        # MLP Side
        mlp_input = torch.cat([user_embeddings, item_embeddings], dim=1)
        mlp_output = self.mlp_layers(mlp_input)

        # Combining MLP & GMF
        final_output = torch.cat([gmf_layer, mlp_output], dim=1)
        final_output = self.output_layer(final_output)

        output = final_output.squeeze()
        return output
