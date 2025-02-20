from kfp.dsl import pipeline


from components.data_load import load_dataset
from components.data_preprocess import preprocess
from components.train_model import train_and_evaluate


@pipeline(
    name="rec-sys-pipeline",
    description="A pipeline that performs loading, preprocessing, training and deploying",
)
def rec_sys_pipeline(
    blob_ratings: str,
    blob_movies: str,
    bucket_name: str,
):
    output_load_data = load_dataset(
        blob_movies=blob_movies, blob_ratings=blob_ratings, bucket_name=bucket_name
    )
    output_movie_dataset = output_load_data.outputs["output_movie_dataset"]
    output_ratings_dataset = output_load_data.outputs["output_ratings_dataset"]

    output_preprocess_data = preprocess(
        input_movies_dataset=output_movie_dataset,
        input_ratings_dataset=output_ratings_dataset,
    )
    n_movies = output_preprocess_data.outputs["number_of_movies"]
    n_users = output_preprocess_data.outputs["number_of_users"]
    train_dataset = output_preprocess_data.outputs["train_ratings_dataset"]
    test_dataset = output_preprocess_data.outputs["test_ratings_dataset"]

    output_model = train_and_evaluate(
        n_movies=n_movies,
        n_users=n_users,
        train_dataset=train_dataset,
        test_dataset=test_dataset,
    )
    model = output_model.outputs["model"]
