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
    import json
    import logging
    import os
    import tempfile

    import pandas as pd
    from rec_sys.model.train import eval_model, load_data_and_train
    from rec_sys.model.utils.handler_export import copy_handler_file
    import torch

    logger = logging.getLogger(__name__)

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
    logger.info(f"The model scripted successfully.")

    # PT file -> MAR file
    with tempfile.TemporaryDirectory(delete=False) as tmpdirname:
        model_path = os.path.join(tmpdirname, "model.pt")
        scripted_model.save(model_path)
        logger.info(f"The model path is: {model_path}. Model saved succefully.")

        handler_path = os.path.join(tmpdirname, "handler.py")
        copy_handler_file(handler_path)
        logger.info(f"The handler path is: {handler_path}. Handler saved succefully.")

        hyperparameters = {"n_movies": 9742, "top_k": 9}
        hyperparameters_path_json = os.path.join(tmpdirname, "hyperparameters.json")
        with open(hyperparameters_path_json, "w") as fp:
            json.dump(hyperparameters, fp)
        logger.info(
            f"The hyperparameter path is: {hyperparameters_path_json}. Hyperparameters saved succefully."
        )

        with open(hyperparameters_path_json) as f:
            d = json.load(f)
            logger.info(f"The hyperparameters are {json.dumps(d)}")

        command = f"""torch-model-archiver --model-name {model_name} --version 1.0 --serialized-file {model_path} --handler {handler_path} --export-path {model_dir} --extra-files {hyperparameters_path_json}"""
        os.system(command)
        logger.info("Command executed successfuly.")

    logger.info(f"Temp directory content {os.listdir(tmpdirname)}")
    if os.path.isdir(model_dir):
        logger.info(f"Main directory content {os.listdir(model_dir)}")
