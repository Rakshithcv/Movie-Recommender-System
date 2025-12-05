# test_recommender.py

import pickle
import pandas as pd

# Load data
movies = pickle.load(open("movies.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# If movies is dict, convert to DataFrame
if isinstance(movies, dict):
    movies = pd.DataFrame(movies)

print("Movies shape:", movies.shape)
print("Similarity shape:", getattr(similarity, "shape", "no shape attr"))


def recommend_core(movie_title: str, top_n: int = 5):
    """Same logic as your app, but without posters (for testing only)."""
    try:
        movie_index = movies[movies["title"] == movie_title].index[0]
    except IndexError:
        # movie not found
        return []

    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        key=lambda x: x[1],
        reverse=True
    )[1:top_n + 1]

    recommended_titles = []
    for idx, score in movie_list:
        recommended_titles.append(movies.iloc[idx]["title"])
    return recommended_titles


def run_basic_tests(sample_size: int | None = None, top_n: int = 5):
    total_movies = len(movies)
    print(f"Total movies: {total_movies}")

    # if sample_size is given, test only a subset
    if sample_size is not None and sample_size < total_movies:
        indices_to_test = range(sample_size)
        print(f"Testing only first {sample_size} movies for speed...")
    else:
        indices_to_test = range(total_movies)
        print("Testing ALL movies...")

    errors = []
    empty_recs = 0

    for i in indices_to_test:
        title = movies.iloc[i]["title"]
        try:
            recs = recommend_core(title, top_n=top_n)
        except Exception as e:
            errors.append((title, str(e)))
            continue

        # Check 1: recommendations list should not be empty
        if len(recs) == 0:
            empty_recs += 1

        # Check 2: recommended titles should exist in 'movies'
        for r in recs:
            if r not in set(movies["title"].values):
                errors.append((title, f"Recommended movie not found in dataset: {r}"))

    print("\n===== TEST SUMMARY =====")
    print(f"Movies tested: {len(list(indices_to_test))}")
    print(f"Movies with EMPTY recommendations: {empty_recs}")
    print(f"Movies with ERRORS: {len(errors)}")

    if errors:
        print("\nSample errors (first 10):")
        for t, err in errors[:10]:
            print(f"- For '{t}': {err}")
    else:
        print("✅ No errors found in recommendation logic!")

    print("========================")


if __name__ == "__main__":
    # For first run, maybe test with 200 to be safe:
    # run_basic_tests(sample_size=200, top_n=5)

    # When confident, uncomment below to test all:
    run_basic_tests(sample_size=None, top_n=5)
