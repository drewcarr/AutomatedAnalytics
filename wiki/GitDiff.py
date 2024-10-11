import subprocess

def get_latest_commit_diff():
    try:
        # Get the latest commit hash
        commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode('utf-8')

        # Check the number of commits in the repository
        commit_count = subprocess.check_output(["git", "rev-list", "--count", "HEAD"]).strip().decode('utf-8')

        # Compare against the parent commit if there are more than one commits
        if commit_count != "1":
            diff = subprocess.check_output(["git", "diff", commit_hash + "^", commit_hash]).decode('utf-8')
        else:
            # For the first commit, show the changes made in that commit
            diff = subprocess.check_output(["git", "show", commit_hash]).decode('utf-8')

        return diff
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None

# Example usage
diff = get_latest_commit_diff()
print(diff)