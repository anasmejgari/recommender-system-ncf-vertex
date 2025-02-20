from kfp.dsl import component, Dataset, Input, Model, Output

from .config import BASE_IMAGE_REC_SYS


@component(
    base_image=BASE_IMAGE_REC_SYS,
    packages_to_install=["joblib", "pandas", "fsspec", "gcsfs"],
)
def train_and_evaluate(
    n_movies: int,
    n_users: int,
    train_dataset: Input[Dataset],
    test_dataset: Input[Dataset],
    model: Output[Model],
    batch_size: int = 64,
    embedding_dim: int = 64,
    learning_rate: float = 0.001,
    epochs: int = 5,
):
    import joblib

    import pandas as pd
    from rec_sys.model.train import eval_model, load_data_and_train

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

    train_df = pd.read_csv(test_dataset.path)
    rmse_test = eval_model(trained_model, train_df)
    model.metadata["framework"] = "PyTorch"
    model.metadata["metrics"] = {"RMSE Training": rmse_training, "RMSE Test": rmse_test}

    file_name = model.path + ".joblib"
    joblib.dump(trained_model, file_name)
