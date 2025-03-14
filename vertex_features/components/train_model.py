from kfp.dsl import component, Dataset, Input, Model, Output

from .config import BASE_IMAGE_REC_SYS


@component(
    base_image=BASE_IMAGE_REC_SYS,
    packages_to_install=["joblib", "pandas", "fsspec", "gcsfs"],
)
def train_and_evaluate(
    n_movies: int,
    n_users: int,
    model_name: str,
    train_dataset: Input[Dataset],
    test_dataset: Input[Dataset],
    model: Output[Model],
    batch_size: int = 64,
    embedding_dim: int = 64,
    learning_rate: float = 0.001,
    epochs: int = 5,
):
    """Train, evaluate and package a MAR archive for the model."""
    import json
    import logging
    import os
    import tempfile

    import pandas as pd
    from rec_sys.model.train import eval_model, load_data_and_train
    from rec_sys.model.utils.handler_export import copy_handler_file
    import torch

    logger = logging.getLogger(__name__)

    # Train the model
    train_df = pd.read_csv(train_dataset.path)
    trained_model, rmse_training = load_data_and_train(
        train_df,
        n_users=n_users,
        n_movies=n_movies,
        embedding_dim=embedding_dim,
        batch_size=batch_size,
        learning_rate=learning_rate,
        epochs=epochs,
    )

    # Evaluate the model
    test_df = pd.read_csv(test_dataset.path)
    rmse_test = eval_model(trained_model, test_df)
    model.metadata["framework"] = "PyTorch"
    model.metadata["metrics"] = json.dumps(
        {"RMSE Training": rmse_training, "RMSE Test": rmse_test}
    )

    # Ensure model directory exists
    model_dir = model.path
    os.makedirs(model_dir, exist_ok=True)
    logger.info(f"The model directory is: {model_dir}")
    if os.path.isdir(model_dir):
        logger.info(f"Directory content {os.listdir(model_dir)}")

    # Save the model
    example_user_tensor = torch.LongTensor([0] * n_movies)
    example_item_tensor = torch.LongTensor(list(range(n_movies)))
    scripted_model = torch.jit.trace(
        trained_model, (example_user_tensor, example_item_tensor)
    )

    # For the endpoint, we need to have a MAR Archive
    # TorchServe needs the MAR File
    # We need: - SerializedFile (.pt) for the model
    #          - Handler(.py) file for PyTorch model
    #          - hyperparameters file
    # They need to be placed in a unique location
    # Then run th torch model archiver command
    with tempfile.TemporaryDirectory(delete=False) as tmpdirname:
        # Serialized file
        model_path = os.path.join(tmpdirname, "model.pt")
        scripted_model.save(model_path)

        # Handler file with BaseHandler class for TochServe
        handler_path = os.path.join(tmpdirname, "handler.py")
        copy_handler_file(handler_path)

        # Hyperparameters file in json format
        hyperparameters = {"n_movies": 9742, "top_k": 9}
        hyperparameters_path_json = os.path.join(tmpdirname, "hyperparameters.json")
        with open(hyperparameters_path_json, "w") as fp:
            json.dump(hyperparameters, fp)

        # Build the MAR archive
        command = " ".join(
            [
                "torch-model-archiver",
                f"--model-name {model_name}",
                f"--version 1.0",
                f"--serialized-file {model_path}",
                f"--handler {handler_path}",
                f"--export-path {model_dir}",
                f"--extra-files {hyperparameters_path_json}",
            ]
        )
        os.system(command)
        logger.info("Command executed successfuly.")
