import os
import glob

def find_files(directory, pattern, recursive=False):
    """
    Finds files matching one or more patterns in a directory (and optionally its subdirectories).

    The pattern can be a single glob-style pattern (e.g., '*.txt') or a
    semicolon-separated string of multiple glob-style patterns
    (e.g., '*.jpg;*.jpeg;*.png').

    Args:
        directory (str): The path to the directory to search.
        pattern (str): A glob-style pattern or a semicolon-separated string of patterns.
        recursive (bool, optional): If True, searches subdirectories as well. Defaults to False.

    Returns:
        list: A list of full path filenames that match any of the provided patterns.
              Returns an empty list if no matching files are found.
    """
    full_paths = []
    patterns = pattern.split(';')
    found_files = set()  # Use a set to avoid duplicates if multiple patterns match the same file

    if recursive:
        for root, _, files in os.walk(directory):
            for filename in files:
                for pat in patterns:
                    if glob.fnmatch.fnmatch(filename, pat.strip()):
                        full_path = os.path.join(root, filename)
                        found_files.add(full_path)
                        break  # Once a match is found for a file, no need to check other patterns
    else:
        for filename in os.listdir(directory):
            full_path = os.path.join(directory, filename)
            if os.path.isfile(full_path):
                for pat in patterns:
                    if glob.fnmatch.fnmatch(filename, pat.strip()):
                        found_files.add(full_path)
                        break  # Once a match is found for a file, no need to check other patterns

    return sorted(list(found_files))  # Return a sorted list for consistency