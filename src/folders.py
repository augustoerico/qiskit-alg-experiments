from datetime import date
from os import listdir
from pathlib import Path


def create_parent_folder() -> str:
    today = date.today().isoformat()
    path = f'experiments/{today}'
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def create_run_folder(path: str) -> str:
    folders = sorted(listdir(path), reverse=True)
    if len(folders) > 0:
        run_index_str = folders[0][len('run-'):]
        run_index = int(run_index_str) + 1
    else:
        run_index = 1
    path = f'{path}/run-{run_index}'
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def create_artifacts_folder():
    parent_folder_path = create_parent_folder()
    run_folder_path = create_run_folder(parent_folder_path)
    return run_folder_path


def main():
    create_artifacts_folder()

if __name__ == '__main__':
    main()
