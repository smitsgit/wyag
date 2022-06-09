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
argsp = subparser.add_parser("init", help="Initialize empty repo")
argsp.add_argument("path",
                   metavar="directory",
                   nargs="?",
                   default=".",
                   help="Where to create directory")


class GitObject:
    repo = None

    def __init__(self, repo, data=None):
        self.repo = repo
        if data:
            self.deserialize(data)

    def serialize(self):
        """
        This function must be implemented by subclasses.
        It must read object's contents from the data which is a byte string
        and do whatever it takes to convert it to a meaningful representation.
        What exactly that means, depends on the subclass
        :return:
        """
        raise Exception("Unimplemented")

    def deserialize(self, data):
        raise Exception("Unimplemented !!")


def obj_read(repo, sha):
    format_class = None
    path = repo.gitdir / "objects" / sha[:2] / sha[2:]
    with open(path, "rb") as file:
        raw = zlib.decompress(file.read())

        # find the format
        space_index = raw.find(b' ')
        format = raw[:space_index]

        # find the size, start looking after the space index
        zero_index = raw.find(b'\x00', space_index)
        size = int(raw[space_index: zero_index].decode('ascii'))
        if size != len(raw) - zero_index - 1:
            raise Exception(f"Malformed object {sha}: bad length")

        match format:
            case b'commit':
                format_class = GitCommit
            case b'tree':
                format_class = GitTree
            case b'tag':
                format_class = GitTag
            case b'blob':
                format_class = GitBlob

        # Call constructor and return object
        return format_class(repo, raw[y + 1:])


class GitRepository:
    """
    A git repository. It has
    1. worktree : path that contains the list of files to get under version control
    2. gitdir: metadata for git itself
    3. conf: configuration for the git
    """

    def __init__(self, path: str, force=False):
        self.worktree = pathlib.Path(path)
        self.gitdir = (self.worktree / ".git")  # type: Path

        if not self.gitdir.exists():
            self.gitdir.mkdir()

        if not (force or self.gitdir.is_dir()):
            raise Exception(f"Not a git repo {path}")

        self.conf_parser = configparser.ConfigParser()
        cf = self.gitdir / "config"
        cf.touch()

        if cf and cf.exists():
            self.conf_parser.read(cf)
        elif not force:
            raise Exception(f"Config file is missing")

        if not force:
            version = int(self.conf_parser.get("core", "repositoryformatversion"))
            if version != 0:
                raise Exception(f"Unsupported repo format version {version}")


def repo_find(path: pathlib.Path):
    while path != Path("/"):
        if (path / ".git").is_dir():
            print(f".git found at {path}")
            return GitRepository(path)
        path = path.parent
    print("Didn't find the repo")
    return None


def repo_create(path: str) -> GitRepository:
    """
    Create a repo at specified path
    :param path:
    :return GitRepository:
    """
    repo = GitRepository(path, True)
    if repo.worktree.exists():
        if not repo.worktree.is_dir():
            raise Exception(f"{path} is not a directory")
        if not list(repo.worktree.iterdir()):
            raise Exception(f"{path} is not empty")
    else:
        repo.worktree.mkdir()

    create_git_dir_structure(repo)

    with open(repo.gitdir / "description", "w") as file:
        file.write("ref: refs/heads/master\n")

    with open(repo.gitdir / "config", "w") as file:
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
    (repo.gitdir / "refs" / "tags").mkdir(parents=True)
    (repo.gitdir / "refs" / "heads").mkdir(parents=True)
    (repo.gitdir / "description").touch()
    (repo.gitdir / "HEAD").touch()


def main(argv=sys.argv[1:]):
    args = parser.parse_args(argv)
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
            cmd_init(args)
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


def cmd_init(args):
    repo = repo_create(args.path)
