import subprocess

def get_latest_commit_diff():
    try:
        # Get the latest commit hash
        commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode('utf-8')

        # Get the diff of the latest commit
        diff = subprocess.check_output(["git", "diff", commit_hash + "^", commit_hash]).decode('utf-8')

        return diff
    except subprocess.CalledProcessError:
        print("Error: The current directory is not a Git repository.")
        exit(1)
