"""
GitHub API integration for fetching public repositories.
"""

import os
import logging
from typing import List, Optional
from datetime import datetime
import requests
from schema import Project


logger = logging.getLogger(__name__)


class GitHubIndexer:
    """Fetch and index public GitHub repositories."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize GitHub indexer.

        Args:
            api_key: GitHub API token. If not provided, will try to load from env.
        """
        self.api_key = api_key or os.getenv("GITHUB_API_KEY")
        if not self.api_key:
            raise ValueError("GitHub API key not provided")

        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.api_key}",
            "Accept": "application/vnd.github.v3+json",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_authenticated_user(self) -> str:
        """Get the authenticated user's username."""
        response = self.session.get(f"{self.base_url}/user")
        response.raise_for_status()
        return response.json()["login"]

    def fetch_public_repos(self, username: Optional[str] = None) -> List[Project]:
        """
        Fetch all public repositories for a user.

        Args:
            username: GitHub username. If not provided, uses authenticated user.

        Returns:
            List of Project objects representing repositories.
        """
        if not username:
            username = self.get_authenticated_user()

        logger.info(f"Fetching public repositories for {username}")

        projects = []
        page = 1
        per_page = 100

        while True:
            url = f"{self.base_url}/users/{username}/repos"
            params = {
                "type": "public",
                "per_page": per_page,
                "page": page,
                "sort": "updated",
            }

            response = self.session.get(url, params=params)
            response.raise_for_status()

            repos = response.json()

            if not repos:
                break

            for repo in repos:
                # Skip private repositories (double-check)
                if repo.get("private", False):
                    continue

                project = Project(
                    source="GitHub",
                    type="Repository",
                    name=repo["name"],
                    full_name=repo["full_name"],
                    description=repo.get("description"),
                    url=repo["html_url"],
                    created_at=datetime.fromisoformat(
                        repo["created_at"].replace("Z", "+00:00")
                    ),
                    updated_at=datetime.fromisoformat(
                        repo["updated_at"].replace("Z", "+00:00")
                    ),
                    language=repo.get("language"),
                    topics=repo.get("topics", []),
                )
                projects.append(project)

            logger.info(f"Fetched page {page} ({len(repos)} repos)")

            # Check if there are more pages
            if len(repos) < per_page:
                break

            page += 1

        logger.info(f"Total public repositories fetched: {len(projects)}")
        return projects

    def fetch_public_gists(self, username: Optional[str] = None) -> List[Project]:
        """
        Fetch all public gists for a user.

        Args:
            username: GitHub username. If not provided, uses authenticated user.

        Returns:
            List of Project objects representing gists.
        """
        if not username:
            username = self.get_authenticated_user()

        logger.info(f"Fetching public gists for {username}")

        projects = []
        page = 1
        per_page = 100

        while True:
            url = f"{self.base_url}/users/{username}/gists"
            params = {
                "per_page": per_page,
                "page": page,
            }

            response = self.session.get(url, params=params)
            response.raise_for_status()

            gists = response.json()

            if not gists:
                break

            for gist in gists:
                # Skip private gists
                if not gist.get("public", True):
                    continue

                # Get gist description or use first filename
                description = gist.get("description")
                if not description and gist.get("files"):
                    first_file = list(gist["files"].keys())[0]
                    description = f"Gist containing {first_file}"

                # Get primary language from first file
                language = None
                if gist.get("files"):
                    first_file_data = list(gist["files"].values())[0]
                    language = first_file_data.get("language")

                project = Project(
                    source="GitHub",
                    type="Gist",
                    name=gist["id"],
                    full_name=f"{username}/gist:{gist['id']}",
                    description=description,
                    url=gist["html_url"],
                    created_at=datetime.fromisoformat(
                        gist["created_at"].replace("Z", "+00:00")
                    ),
                    updated_at=datetime.fromisoformat(
                        gist["updated_at"].replace("Z", "+00:00")
                    ),
                    language=language,
                    topics=[],  # Gists don't have topics
                )
                projects.append(project)

            logger.info(f"Fetched page {page} ({len(gists)} gists)")

            # Check if there are more pages
            if len(gists) < per_page:
                break

            page += 1

        logger.info(f"Total public gists fetched: {len(projects)}")
        return projects

    def check_rate_limit(self) -> dict:
        """Check current API rate limit status."""
        response = self.session.get(f"{self.base_url}/rate_limit")
        response.raise_for_status()
        return response.json()
