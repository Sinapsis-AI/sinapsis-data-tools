# -*- coding: utf-8 -*-

from pathlib import Path


def is_regex(fpath: str) -> bool:
    """
    Determine if the fiven path contains the character (*) indicating that it might be a regular
    expresion or a glob pattern.
    Args:
        fpath (str): the file path to check
    Returns
        (bool): True if the character is in the pattern, false otherwise.

    """
    return "*" in fpath


SUPPORTED_VIDEO_TYPE_EXT = ["mp4", "wav", "mov"]


def process_single_path(single_path: str) -> list[str]:
    """Determines all the paths to be visited according to the single
    path provided

    Args:
        single_path (str): single path provided

    Returns:
        list[str]: List of all the paths to be visited when processing the data
    """
    video_file_paths: list[str] = []

    if is_regex(single_path):
        search_pattern_start = single_path.find("*")
        search_pattern_end = single_path.rfind("*")
        root_dir = single_path[0:search_pattern_start]
        pattern = single_path[search_pattern_end:]
        video_file_paths += [str(f.resolve()) for f in Path(root_dir).glob(pattern)]

    elif "." in single_path and single_path.split(".")[-1].lower() in SUPPORTED_VIDEO_TYPE_EXT:
        video_file_paths = [single_path]

    elif Path(single_path).is_dir():
        for vid_type in SUPPORTED_VIDEO_TYPE_EXT:
            video_file_paths += [str(f.resolve()) for f in Path(single_path).glob(f"**/*{vid_type}")]

    return video_file_paths


def parse_file_paths(file_paths: str | list[str]) -> list[str]:
    """
    Check if the path provided is a single path or a list of paths.
    If it's a single path, parse the content inside.
    If it's a list of paths, loop though the list and parse each of them.

    Args:
        file_paths (str | list[str]): path or list of paths to parse.

    Returns:
        list[str]: list of complete paths to process
    """
    return_file_paths: list[str] = []
    if isinstance(file_paths, str):
        return_file_paths += process_single_path(file_paths)
    elif isinstance(file_paths, list):
        for file_path in file_paths:
            return_file_paths += process_single_path(file_path)
    return return_file_paths
