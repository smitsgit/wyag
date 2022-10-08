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
subparser.required = True

argsp = subparser.add_parser("init", help="Initialize empty repo")
argsp.add_argument("path",
                   metavar="directory",
                   nargs="?",
                   default=".",
                   help="Where to create directory")

argsp = subparser.add_parser("cat-file",
                             help="Provide content of repository objects")

argsp.add_argument("type",
                   metavar="type",
                   choices=["blob", "commit", "tag", "tree"],
                   help="Specify the type")

argsp.add_argument("object",
                   metavar="object",
                   help="The object to display")

argsp = subparser.add_parser(
    "hash-object",
    help="Compute object ID and optionally creates a blob from a file")

argsp.add_argument("-t",
                   metavar="type",
                   dest="type",
                   choices=["blob", "commit", "tag", "tree"],
                   default="blob",
                   help="Specify the type")

argsp.add_argument("-w",
                   dest="write",
                   action="store_true",
                   help="Actually write the object into the database")

argsp.add_argument("path",
                   help="Read object from <file>")


argsp = subparser.add_parser("log", help="Display history of a given commit.")
argsp.add_argument("commit",
                   default="HEAD",
                   nargs="?",
                   help="Commit to start at.")

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


class GitBlob(GitObject):
    fmt = b'blob'

    def serialize(self):
        return self.blobdata

    def deserialize(self, data):
        self.blobdata = data


def obj_find(repo, name, fmt=None, follow=True):
    """
    The reason for this strange small function is that Git has a lot of ways to refer to objects:
    full hash, short hash, tags… object_find() will be our name resolution function.
    We’ll only implement it later, so this is a temporary placeholder.
    This means that until we implement the real thing, the only way we can refer to
    an object will be by its full hash.
    :param repo:
    :param name:
    :param fmt:
    :param follow:
    :return:
    """
    return name


def obj_read(repo, sha):
    """
    This function returns objects from the sha1
    """
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
            # case b'tree':
            #     format_class = GitTree
            # case b'tag':
            #     format_class = GitTag
            case b'blob':
                format_class = GitBlob

        # Call constructor and return object
        return format_class(repo, raw[zero_index + 1:])


def obj_write(obj, actually_write=True):
    """
    This function writes sha1 for a given object
    """
    # serialize the object
    data = obj.serialize()
    # Add the header
    result = obj.fmt + b' ' + str(len(data)).encode() + b'\x00' + data

    # compute the hash
    sha = hashlib.sha1(result).hexdigest()

    if actually_write:
        # compute the path
        path = obj.repo.gitdir / "objects" / sha[:2]
        path.mkdir(parents=True, exist_ok=True)
        path = path / sha[2:]
        with open(path, "wb") as file:
            file.write(zlib.compress(result))
    return sha


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
            self.gitdir.mkdir(parents=True, exist_ok=True)

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


def repo_find(path: pathlib.Path = pathlib.Path(".")):
    while path != pathlib.Path("/"):
        if (path / ".git").is_dir():
            print(f".git found at {path}")
            print("#" * 16)
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
        file.write("Unnamed repository; edit this file 'description' to name the repository.\n")

    with open(repo.gitdir / "HEAD", "w") as file:
        file.write("ref: refs/heads/master\n")

    with open(repo.gitdir / "config", "w") as file:
        config_parser = repo_default_config()  # type: configparser.ConfigParser
        config_parser.write(file)

    return repo


def repo_default_config() -> configparser.ConfigParser:
    config_parser = configparser.ConfigParser()
    config_parser.add_section("core")
    config_parser.set("core", "repositoryformatversion", "0")
    config_parser.set("core", "filemode", "false")
    config_parser.set("core", "bare", "false")
    return config_parser


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
            cmd_cat_file(args)
        case "checkout":
            pass
        case "commit":
            pass
        case "hash-object":
            cmd_hash_object(args)
        case "init":
            cmd_init(args)
        case "log":
            cmd_log(args)
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


def cmd_cat_file(args):
    path = pathlib.Path(".").absolute()
    repo = repo_find(path)
    cat_file(repo, args.object, fmt=args.type.encode())


def cat_file(repo, obj_name, fmt):
    obj = obj_read(repo, obj_find(repo, obj_name, fmt=fmt))
    sys.stdout.buffer.write(obj.serialize())


def cmd_hash_object(args):
    if args.write:
        repo = GitRepository(".")
    else:
        repo = None

    with open(args.path, "rb") as fd:
        sha = object_hash(fd, args.type.encode(), repo)
        print(sha)


def object_hash(fd, fmt, repo=None):
    data = fd.read()

    # Choose constructor depending on
    # object type found in header.
    if fmt == b'blob':
        obj = GitBlob(repo, data)
    # elif fmt == b'tree':
    #     obj = GitTree(repo, data)
    # elif fmt == b'tag':
    #     obj = GitTag(repo, data)
    # elif fmt == b'commit':
    #     obj = GitCommit(repo, data)
    else:
        raise Exception("Unknown type %s!" % fmt)

    return obj_write(obj, repo)


def kvlm_parse(raw, start=0, dct=None):
    if not dct:
        dct = collections.OrderedDict()
        # You CANNOT declare the argument as dct=OrderedDict() or all
        # call to the functions will endlessly grow the same dict.

    # We search for the next space and the next newline.
    spc = raw.find(b' ', start)
    nl = raw.find(b'\n', start)

    # If space appears before newline, we have a keyword.

    # Base case
    # =========
    # If newline appears first (or there's no space at all, in which
    # case find returns -1), we assume a blank line.  A blank line
    # means the remainder of the data is the message.
    if (spc < 0) or (nl < spc):
        assert (nl == start)
        dct[b''] = raw[start + 1:]
        return dct

    # Recursive case
    # ==============
    # we read a key-value pair and recurse for the next.
    key = raw[start:spc]

    # Find the end of the value.  Continuation lines begin with a
    # space, so we loop until we find a "\n" not followed by a space.
    end = start
    while True:
        end = raw.find(b'\n', end + 1)
        if raw[end + 1] != ord(' '): break

    # Grab the value
    # Also, drop the leading space on continuation lines
    value = raw[spc + 1:end].replace(b'\n ', b'\n')

    # Don't overwrite existing data contents
    if key in dct:
        if type(dct[key]) == list:
            dct[key].append(value)
        else:
            dct[key] = [dct[key], value]
    else:
        dct[key] = value

    return kvlm_parse(raw, start=end + 1, dct=dct)


def kvlm_serialize(kvlm):
    ret = b''

    # Output fields
    for k in kvlm.keys():
        # Skip the message itself
        if k == b'': continue
        val = kvlm[k]
        # Normalize to a list
        if type(val) != list:
            val = [val]

        for v in val:
            ret += k + b' ' + (v.replace(b'\n', b'\n ')) + b'\n'

    # Append message
    ret += b'\n' + kvlm[b'']

    return ret


class GitCommit(GitObject):
    fmt=b'commit'

    def deserialize(self, data):
        self.kvlm = kvlm_parse(data)

    def serialize(self):
        return kvlm_serialize(self.kvlm)


def cmd_log(args):
    repo = repo_find()

    print("digraph wyaglog{")
    log_graphviz(repo, obj_find(repo, args.commit), set())
    print("}")

def log_graphviz(repo, sha, seen):

    if sha in seen:
        return
    seen.add(sha)

    commit = obj_read(repo, sha)
    assert (commit.fmt==b'commit')

    if not b'parent' in commit.kvlm.keys():
        # Base case: the initial commit.
        return

    parents = commit.kvlm[b'parent']

    if type(parents) != list:
        parents = [ parents ]

    for p in parents:
        p = p.decode("ascii")
        print ("c_{0} -> c_{1};".format(sha, p))
        log_graphviz(repo, p, seen)