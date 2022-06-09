import collections
import argparse
import configparser
import hashlib  # Git uses sha-1 explicitly
import pathlib
import re
import sys
import zlib  # Git compresses everything using ZLIB

parser = argparse.ArgumentParser(description="Its just a content tracker")
subparser = parser.add_subparsers(title="Commands", dest="command")


class GitRepository:
    """
    A git repository. It has
    1. worktree : path that contains the list of files to get under version control
    2. gitdir: metadata for git itself
    3. conf: configuration for the git
    """

    def __init__(self, path: str, force=False):
        self.worktree = pathlib.Path(path)
        self.gitdir = self.worktree / ".git"  # type: Path

        if not (force or self.gitdir.is_dir()):
            raise Exception(f"Not a git repo {path}")

        self.conf_parser = configparser.ConfigParser()
        cf = self.gitdir / "config"

        if cf and cf.exists():
            self.conf_parser.read(cf)
        elif not force:
            raise Exception(f"Config file is missing")

        if not force:
            version = int(self.conf_parser.get("core", "repositoryformatversion"))
            if version != 0:
                raise Exception(f"Unsupported repo format version {version}")


def repo_create(path: str) -> GitRepository:
    """
    Create a repo at specified path
    :param path:
    :return GitRepository:
    """
    repo = GitRepository(path)
    if repo.worktree.exists():
        if not repo.worktree.is_dir():
            raise Exception(f"{path} is not a directory")
        if not list(repo.worktree.iterdir()):
            raise Exception(f"{path} is not empty")
    else:
        repo.worktree.mkdir()

    create_git_dir_structure(repo)

    with open(repo.gitdir / "description") as file:
        file.write("ref: refs/heads/master\n")

    with open(repo.gitdir / "config") as file:
        config = repo_default_config()  # type: configparser.ConfigParser
        config.write(file)

    return repo


def repo_default_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.add_section("core")
    config.set("core", "repositoryformatversion", "0")
    config.set("core", "filemode", "false")
    config.set("core", "bare", "false")
    return config


def create_git_dir_structure(repo):
    (repo.gitdir / "branches").mkdir()
    (repo.gitdir / "objects").mkdir()
    (repo.gitdir / "refs" / "tags").mkdir()
    (repo.gitdir / "refs" / "heads").mkdir()
    (repo.gitdir / "description").touch()
    (repo.gitdir / "HEAD").touch()


def main(argv=sys.argv[1:]):
    args = parser.parse_args(argv)
    print("Hello World!!!")
    match args.command:
        case "add":
            pass
        case "cat-file":
            pass
        case "checkout":
            pass
        case "commit":
            pass
        case "hash-object":
            pass
        case "init":
            pass
        case "log":
            pass
        case "ls-tree":
            pass
        case "merge":
            pass
        case "rebase":
            pass
        case "rev-parse":
            pass
        case "rm":
            pass
        case "show-ref":
            pass
        case "tag":
            pass
