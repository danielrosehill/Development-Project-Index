"""
Hugging Face API integration for fetching public models, datasets, and spaces.
"""

import os
import logging
from typing import List, Optional
from datetime import datetime
import requests
from schema import Project


logger = logging.getLogger(__name__)


class HuggingFaceIndexer:
    """Fetch and index public Hugging Face resources."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Hugging Face indexer.

        Args:
            api_key: HuggingFace API token. If not provided, will try to load from env.
        """
        self.api_key = api_key or os.getenv("HF_CLI")
        if not self.api_key:
            raise ValueError("Hugging Face API key not provided")

        self.base_url = "https://huggingface.co/api"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_authenticated_user(self) -> str:
        """Get the authenticated user's username."""
        response = self.session.get(f"{self.base_url}/whoami-v2")
        response.raise_for_status()
        return response.json()["name"]

    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string from HF API."""
        if not date_str:
            return None
        try:
            # HF uses ISO format
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None

    def fetch_public_models(self, author: Optional[str] = None) -> List[Project]:
        """
        Fetch all public models for an author.

        Args:
            author: HuggingFace username. If not provided, uses authenticated user.

        Returns:
            List of Project objects representing models.
        """
        if not author:
            author = self.get_authenticated_user()

        logger.info(f"Fetching public models for {author}")

        projects = []
        url = f"{self.base_url}/models"
        params = {
            "author": author,
            "limit": 500,  # HF allows up to 500
        }

        response = self.session.get(url, params=params)
        response.raise_for_status()
        models = response.json()

        for model in models:
            # Skip private models
            if model.get("private", False):
                continue

            project = Project(
                source="HuggingFace",
                type="Model",
                name=model["id"].split("/")[-1] if "/" in model["id"] else model["id"],
                full_name=model["id"],
                description=model.get("cardData", {}).get("description") or model.get("description"),
                url=f"https://huggingface.co/{model['id']}",
                created_at=self._parse_datetime(model.get("createdAt")),
                updated_at=self._parse_datetime(model.get("lastModified")),
                language=model.get("pipeline_tag"),  # Using pipeline_tag as language
                topics=model.get("tags", []),
            )
            projects.append(project)

        logger.info(f"Total public models fetched: {len(projects)}")
        return projects

    def fetch_public_datasets(self, author: Optional[str] = None) -> List[Project]:
        """
        Fetch all public datasets for an author.

        Args:
            author: HuggingFace username. If not provided, uses authenticated user.

        Returns:
            List of Project objects representing datasets.
        """
        if not author:
            author = self.get_authenticated_user()

        logger.info(f"Fetching public datasets for {author}")

        projects = []
        url = f"{self.base_url}/datasets"
        params = {
            "author": author,
            "limit": 500,
        }

        response = self.session.get(url, params=params)
        response.raise_for_status()
        datasets = response.json()

        for dataset in datasets:
            # Skip private datasets
            if dataset.get("private", False):
                continue

            project = Project(
                source="HuggingFace",
                type="Dataset",
                name=dataset["id"].split("/")[-1] if "/" in dataset["id"] else dataset["id"],
                full_name=dataset["id"],
                description=dataset.get("cardData", {}).get("description") or dataset.get("description"),
                url=f"https://huggingface.co/datasets/{dataset['id']}",
                created_at=self._parse_datetime(dataset.get("createdAt")),
                updated_at=self._parse_datetime(dataset.get("lastModified")),
                language=None,
                topics=dataset.get("tags", []),
            )
            projects.append(project)

        logger.info(f"Total public datasets fetched: {len(projects)}")
        return projects

    def fetch_public_spaces(self, author: Optional[str] = None) -> List[Project]:
        """
        Fetch all public spaces for an author.

        Args:
            author: HuggingFace username. If not provided, uses authenticated user.

        Returns:
            List of Project objects representing spaces.
        """
        if not author:
            author = self.get_authenticated_user()

        logger.info(f"Fetching public spaces for {author}")

        projects = []
        url = f"{self.base_url}/spaces"
        params = {
            "author": author,
            "limit": 500,
        }

        response = self.session.get(url, params=params)
        response.raise_for_status()
        spaces = response.json()

        for space in spaces:
            # Skip private spaces
            if space.get("private", False):
                continue

            project = Project(
                source="HuggingFace",
                type="Space",
                name=space["id"].split("/")[-1] if "/" in space["id"] else space["id"],
                full_name=space["id"],
                description=space.get("cardData", {}).get("description") or space.get("description"),
                url=f"https://huggingface.co/spaces/{space['id']}",
                created_at=self._parse_datetime(space.get("createdAt")),
                updated_at=self._parse_datetime(space.get("lastModified")),
                language=space.get("sdk"),  # Gradio, Streamlit, etc.
                topics=space.get("tags", []),
            )
            projects.append(project)

        logger.info(f"Total public spaces fetched: {len(projects)}")
        return projects

    def fetch_all(self, author: Optional[str] = None) -> List[Project]:
        """
        Fetch all public resources (models, datasets, spaces) for an author.

        Args:
            author: HuggingFace username. If not provided, uses authenticated user.

        Returns:
            Combined list of all Project objects.
        """
        all_projects = []

        try:
            all_projects.extend(self.fetch_public_models(author))
        except Exception as e:
            logger.error(f"Error fetching models: {e}")

        try:
            all_projects.extend(self.fetch_public_datasets(author))
        except Exception as e:
            logger.error(f"Error fetching datasets: {e}")

        try:
            all_projects.extend(self.fetch_public_spaces(author))
        except Exception as e:
            logger.error(f"Error fetching spaces: {e}")

        return all_projects
