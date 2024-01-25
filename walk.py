import os


def recursive_walk(directory: str):
    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith(".mp4"):
                yield os.path.join(root, file_name)
