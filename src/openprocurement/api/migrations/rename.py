#!/usr/bin/env python3
import argparse
import os
import subprocess
from pathlib import Path

EXCLUDED_FILES = [
    '__init__.py',
    'base.py',
    'rename.py',
]


def get_files_by_git_order(directory):
    try:
        # Get the git root directory
        cmd_root = ['git', 'rev-parse', '--show-toplevel']
        result_root = subprocess.run(cmd_root, cwd=directory, capture_output=True, text=True, check=True)
        git_root = Path(result_root.stdout.strip())

        # Get relative path from git root to target directory
        rel_path = Path(directory).resolve().relative_to(git_root)

        # Use git log to get files ordered by their first appearance
        cmd = ['git', 'log', '--reverse', '--format=%H', '--', str(rel_path)]
        commits = subprocess.run(cmd, cwd=git_root, capture_output=True, text=True, check=True).stdout.splitlines()

        seen_files = set()
        ordered_files = []

        for commit in commits:
            cmd = ['git', 'ls-tree', '-r', '--name-only', commit, str(rel_path)]
            files = subprocess.run(cmd, cwd=git_root, capture_output=True, text=True, check=True).stdout.splitlines()

            for f in files:
                file_path = Path(f)
                file_name = file_path.name
                # Only include .py files and exclude predefined
                if file_path.suffix == '.py' and file_name not in seen_files and file_name not in EXCLUDED_FILES:
                    seen_files.add(file_name)
                    ordered_files.append(file_path)

        print(f"Found {len(ordered_files)} Python files in git (excluding base.py and __init__.py)")
        return ordered_files
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e.stderr}")
        # Fallback to sorting by creation time if git fails
        files = [f for f in Path(directory).glob('*.py') if f.name not in ['base.py', '__init__.py']]
        return sorted(files, key=lambda x: x.stat().st_ctime)


def rename_files(directory):
    dir_path = Path(directory).resolve()
    print(f"Processing directory: {dir_path}")

    if not dir_path.exists():
        raise Exception(f"Directory {dir_path} does not exist")

    files = get_files_by_git_order(dir_path)

    if not files:
        print("No files found to rename!")
        return

    # Find the highest existing number
    counter = 1
    for file_path in dir_path.glob('*.py'):
        if file_path.name[:4].isdigit() and file_path.name[4] == '_':
            counter = max(counter, int(file_path.name[:4]) + 1)

    print(f"Starting counter from: {counter:04d}")

    for file_path in files:
        full_path = dir_path / file_path.name

        if full_path.is_file():
            filename = full_path.name

            # Skip files that already have the correct numeric prefix pattern
            if filename[:4].isdigit() and filename[4] == '_':
                print(f"Skipping already numbered file: {filename}")
                continue

            new_filename = f"{counter:04d}_{filename}"
            new_path = full_path.parent / new_filename

            print(f"Renaming: {filename} -> {new_filename}")

            try:
                full_path.rename(new_path)
                counter += 1
            except Exception as e:
                print(f"Error renaming {filename}: {e}")


def main():
    parser = argparse.ArgumentParser(description='Rename files by adding counter prefix')
    parser.add_argument('directory', help='Directory path containing files to rename')

    args = parser.parse_args()

    try:
        rename_files(args.directory)
        print("File renaming completed successfully")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
