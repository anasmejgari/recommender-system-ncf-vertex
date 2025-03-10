"""Module to handle the model for TorcheServe."""

from typing import Any

import numpy as np
import torch
from ts.torch_handler.base_handler import BaseHandler


class ModelHandler(BaseHandler):
    """A custom model handler implementation."""

    def initialize(self, context) -> None:
        """Initialize model. This will be called during model loading time.

        Args:
            context: Initial context contains model server system properties.
        """
        model_dir = context.system_properties.get("model_dir")
        self.model = torch.jit.load(f"{model_dir}/model.pt")
        self.model.eval()

        # Fetch parameters from model configuration (if available)
        self.n_movies = 9742  # Default: 100
        self.top_k = 9  # Default: 6
        # TODO Load mapping from GCS

        print(f"Model initialized with n_movies={self.n_movies}, top_k={self.top_k}")
        self.initialized = True

    def preprocess(self, data: list[dict]) -> tuple[torch.LongTensor, torch.LongTensor]:
        """Preprocess Input data.

        Args:
            data (list[dict]): User input

        Raises:
            ValueError: Error of loading data

        Returns:
            tuple[torch.LongTensor, torch.LongTensor] : User, movie tuples
        """
        # Take output from network and post-process to desired format
        user_id = data[0].get("id")  # Assuming input JSON has an 'id' field
        if user_id is None:
            raise ValueError("Input JSON must contain an 'id' field")

        user_tensor = torch.LongTensor(
            [user_id] * self.n_movies
        )  # n_movies copies of user_id
        item_tensor = torch.LongTensor(
            list(range(self.n_movies))
        )  # Item indices from 0 to n_movies-1

        return (user_tensor, item_tensor)

    def inference(
        self, inputs: tuple[torch.LongTensor, torch.LongTensor]
    ) -> list[float]:
        """Inference model.

        Args:
            inputs (tuple[torch.LongTensor, torch.LongTensor]): List of inputs

        Returns:
            list[float]: _description_
        """
        with torch.no_grad():
            outputs = self.model(*inputs)  # Call model with (user_tensor, item_tensor)
        return list(outputs.cpu().numpy().tolist())

    def postprocess(self, predictions: list[float]) -> list[int]:
        """Predict.

        Args:
            predictions (list[float]): Predictions

        Returns:
            list[int]: _description_
        """
        predictions_idx = list(map(int, np.argsort(predictions)[::-1][: self.top_k]))
        # predictions = [
        #     prediction
        #     for prediction in predictions
        #     if prediction not in known_user_items
        # ]
        return predictions_idx

    def handle(self, data: Any, context: Any) -> list[int]:
        """Handler.

        Args:
            data (Any): _description_
            context (Any): _description_

        Returns:
            _type_: _description_
        """
        model_input = self.preprocess(data)
        model_output = self.inference(model_input)
        return self.postprocess(model_output)
