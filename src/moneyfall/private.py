from pathlib import Path


def private_path(path,repo):
    resolved=Path(path).expanduser().resolve()
    if resolved.is_relative_to(Path(repo).resolve()):
        raise ValueError('Private output must live outside the public checkout')
    return resolved
