# prepare_submission.py
#
# ICS 33 Fall 2022
# Project 2: Learning to Fly
#
# Run this script when you're ready to submit your work.  It will create a Git
# bundle from the Git repository in your project directory, which is the one and
# only file we'll accept as a submission.

from collections.abc import Iterable
import os
from pathlib import Path
import subprocess



# If you've installed Git, but it's not in a directory that's listed in your
# operating system's PATH environment variable, replace this value with a string
# that specifies the full path to the Git executable (e.g., "git.exe" on Windows
# or "git" on other operating systems).
_GIT_EXECUTABLE_PATH: str | None
_GIT_EXECUTABLE_PATH = None

# When searching for a Git installation, these are the names of the files for
# which we'll search.
_GIT_EXECUTABLE_NAMES: list[str]
_GIT_EXECUTABLE_NAMES = ['git.exe', 'git']

# This is the name of the submission bundle that will be created.
_BUNDLE_NAME: str
_BUNDLE_NAME = 'project2.bundle'



class MisconfiguredGitExecutableError(Exception):
    pass



class MissingGitExecutableError(Exception):
    pass



def _find_search_directory_paths() -> Iterable[Path]:
    """Finds the paths to all directories in the PATH environment variable."""
    return (Path(directory) for directory in os.environ.get('PATH', '').split(os.pathsep))


def _find_git_executable_paths(directory_path: Path) -> Iterable[Path]:
    """Given the path to a directory, returns the paths to all possible Git
    executables that might be in that directory."""
    return ((directory_path / name) for name in _GIT_EXECUTABLE_NAMES)


def _is_executable(file_path: Path) -> bool:
    """Returns True if the given path is an executable file, or False otherwise."""
    return file_path.is_file() and os.access(file_path, os.X_OK)


def _find_git_executable() -> Path:
    """Finds the Git executable, by either using the one that was configured in the
    _GIT_EXECUTABLE_PATH global variable, or by searching the directories listed in
    the operating system's PATH environment variable."""
    if _GIT_EXECUTABLE_PATH is not None:
        if _is_executable(Path(_GIT_EXECUTABLE_PATH)):
            return Path(_GIT_EXECUTABLE_PATH)
        else:
            raise MisconfiguredGitExecutableError
    else:
        for search_directory_path in _find_search_directory_paths():
            for executable_path in _find_git_executable_paths(search_directory_path):
                if _is_executable(executable_path):
                    return executable_path

        raise MissingGitExecutableError


def _make_working_directory_path() -> Path:
    """Returns the working directory to be used when executing Git."""
    return Path(__file__).parent


def _make_bundle_path() -> Path:
    """Returns the path to the bundle file that should be created by this script."""
    return _make_working_directory_path() / _BUNDLE_NAME


def _is_git_repository_directory(path: Path) -> bool:
    """Returns True if the given path leads to a directory that appears to be a Git
    repository, or False otherwise."""
    return path.is_dir() and (path / '.git').is_dir()


def _has_uncommitted_changes(
        git_executable_path: Path,
        working_directory_path: Path) -> bool:
    """Returns True if there are uncommitted changes in the working directory, or
    False otherwise."""

    # Check for staged but uncommitted changes.
    result = subprocess.run(
        [git_executable_path, 'diff-index', '--quiet', '--cached', 'HEAD', '--'],
        cwd = working_directory_path, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)

    if result.returncode != 0:
        return True

    # Check for changes that have been neither staged nor committed.
    result = subprocess.run(
        [git_executable_path, 'diff-index', '--quiet', 'HEAD', '--'],
        cwd = working_directory_path, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)

    return result.returncode != 0


def _confirm_creation() -> bool:
    """Asks the user to confirm whether they'd like to create a bundle despite
    a warning, returning True if so and False otherwise."""
    confirmation = input('Would you like to create a bundle for submission anyway (Y or N)? ')
    return confirmation.upper().startswith('Y')


def _create_bundle(
        git_executable_path: Path,
        working_directory_path: Path,
        bundle_path: Path) -> None:
    """Calls into the Git executable to create a bundle."""
    print('Creating a bundle for your submission ...')
    print()

    result = subprocess.run(
        [git_executable_path, 'bundle', 'create', bundle_path, '--all'],
        cwd = working_directory_path, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)

    print()

    if result.returncode != 0:
        print(f'"git bundle" return code was {result.returncode}, which suggests that it failed')
    elif not bundle_path.is_file():
        print('After running "git bundle", the bundle file does not appear to exist in the')
        print('location where it was expected to be created, which suggests that it failed.')
    else:
        print('Your submission bundle was created here:')
        print(f'    {bundle_path}')


def main() -> None:
    """The main function that orchestrates the script's execution."""

    try:
        git_executable_path = _find_git_executable()
    except MisconfiguredGitExecutableError:
        print('It appears that you modified this script to specify the location of your')
        print('Git executable by filling in a value for _GIT_EXECUTABLE_PATH, but the')
        print('value you specified is not the path to a file that is executable.')
        return
    except MissingGitExecutableError:
        print('Git is either not installed on this machine, or it is installed in a directory')
        print('that is not listed in your PATH environment variable, which means this script')
        print('does not know where to find it.  You either need to make sure the PATH')
        print('environment variable includes the directory where you installed Git, or')
        print('you can change the value of _GIT_EXECUTABLE_PATH in this script to be the')
        print('location of the Git executable.')
        return

    working_directory_path = _make_working_directory_path()
    bundle_path = _make_bundle_path()

    if not _is_git_repository_directory(working_directory_path):
        print('There is no Git repository in the project directory:')
        print(f'    {working_directory_path}')
        return

    if bundle_path.exists():
        print('There is already a bundle file at the path below, which is presumably from')
        print('a previous execution of this script.  Creating a new one will replace the')
        print('one you already have.')
        print(f'    {bundle_path}')

        if not _confirm_creation():
            return

    if _has_uncommitted_changes(git_executable_path, working_directory_path):
        print('There are changes in your project directory that have not yet been committed')
        print('to the Git repository, so your submission bundle would not be identical to')
        print('the files in your project directory.')

        if not _confirm_creation():
            return

    _create_bundle(git_executable_path, working_directory_path, bundle_path)



if __name__ == '__main__':
    main()
