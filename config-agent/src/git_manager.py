import datetime
import os
from dataclasses import dataclass

from github import Github
from github.GithubException import GithubException


@dataclass
class GitManager:
    token_env_key: str = "GITHUB_TOKEN"

    def _client(self) -> Github:
        token = os.getenv(self.token_env_key)
        if not token:
            raise ValueError(f"Missing env var: {self.token_env_key}")
        return Github(token)

    def create_empty_branch(
        self,
        repo_full_name: str,
        base_branch: str = "main",
        prefix: str = "fix/config-auto",
        timestamp: str | None = None,
    ) -> str:
        """
        Create a new branch pointing to base_branch's latest commit.
        Returns the created branch name.
        """
        client = self._client()
        repo = client.get_repo(repo_full_name)

        if timestamp is None:
            timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")

        branch_name = f"{prefix}-{timestamp}"
        base = repo.get_branch(base_branch)

        try:
            repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base.commit.sha)
        except GithubException as exc:
            raise RuntimeError(
                f"Failed to create branch '{branch_name}' from '{base_branch}': {exc}"
            ) from exc

        return branch_name
