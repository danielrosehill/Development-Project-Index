#!/usr/bin/env python3
"""
Main script to index public projects from GitHub and Hugging Face.

This script fetches all public repositories, models, datasets, and spaces,
and creates a unified JSON index.
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

from schema import ProjectIndex
from github_indexer import GitHubIndexer
from huggingface_indexer import HuggingFaceIndexer


# Setup logging (will be configured in main())
logger = logging.getLogger(__name__)


def load_existing_index(output_file: Path) -> Optional[ProjectIndex]:
    """
    Load existing index from file if it exists.

    Args:
        output_file: Path to the JSON output file.

    Returns:
        ProjectIndex object if file exists and is valid, None otherwise.
    """
    if not output_file.exists():
        return None

    try:
        with open(output_file, "r") as f:
            data = json.load(f)
        # Reconstruct ProjectIndex from JSON
        index = ProjectIndex(**data)
        logger.info(f"Loaded existing index with {len(index.projects)} projects")
        return index
    except Exception as e:
        logger.warning(f"Could not load existing index: {e}")
        return None


def save_index(index: ProjectIndex, output_file: Path) -> None:
    """
    Save the index to a JSON file.

    Args:
        index: ProjectIndex object to save.
        output_file: Path to the JSON output file.
    """
    # Update metadata
    index.metadata["generated_at"] = datetime.now().isoformat()
    index.metadata["total_projects"] = len(index.projects)

    # Count by source
    github_count = len(index.get_by_source("GitHub"))
    hf_count = len(index.get_by_source("HuggingFace"))

    index.metadata["sources"] = {
        "GitHub": github_count,
        "HuggingFace": hf_count,
    }

    # Count by type
    type_counts = {}
    for project in index.projects:
        type_counts[project.type] = type_counts.get(project.type, 0) + 1

    index.metadata["types"] = type_counts

    # Write to file
    with open(output_file, "w") as f:
        f.write(index.to_json())

    logger.info(f"Index saved to {output_file}")
    logger.info(f"Total projects: {len(index.projects)}")
    logger.info(f"  GitHub: {github_count}")
    logger.info(f"  HuggingFace: {hf_count}")


def create_organized_output(index: ProjectIndex, output_dir: Path) -> None:
    """
    Create organized output files by source and type.

    Args:
        index: ProjectIndex object.
        output_dir: Directory to store organized output files.
    """
    output_dir.mkdir(exist_ok=True)

    # GitHub repositories
    github_repos = [p for p in index.projects if p.source == "GitHub" and p.type == "Repository"]
    if github_repos:
        github_file = output_dir / "github_repositories.json"
        with open(github_file, "w") as f:
            json.dump([p.model_dump() for p in github_repos], f, indent=2, default=str)
        logger.info(f"Saved {len(github_repos)} GitHub repositories to {github_file}")

    # GitHub gists
    github_gists = [p for p in index.projects if p.source == "GitHub" and p.type == "Gist"]
    if github_gists:
        gists_file = output_dir / "github_gists.json"
        with open(gists_file, "w") as f:
            json.dump([p.model_dump() for p in github_gists], f, indent=2, default=str)
        logger.info(f"Saved {len(github_gists)} GitHub gists to {gists_file}")

    # HuggingFace Models
    hf_models = [p for p in index.projects if p.source == "HuggingFace" and p.type == "Model"]
    if hf_models:
        models_file = output_dir / "huggingface_models.json"
        with open(models_file, "w") as f:
            json.dump([p.model_dump() for p in hf_models], f, indent=2, default=str)
        logger.info(f"Saved {len(hf_models)} HuggingFace models to {models_file}")

    # HuggingFace Datasets
    hf_datasets = [p for p in index.projects if p.source == "HuggingFace" and p.type == "Dataset"]
    if hf_datasets:
        datasets_file = output_dir / "huggingface_datasets.json"
        with open(datasets_file, "w") as f:
            json.dump([p.model_dump() for p in hf_datasets], f, indent=2, default=str)
        logger.info(f"Saved {len(hf_datasets)} HuggingFace datasets to {datasets_file}")

    # HuggingFace Spaces
    hf_spaces = [p for p in index.projects if p.source == "HuggingFace" and p.type == "Space"]
    if hf_spaces:
        spaces_file = output_dir / "huggingface_spaces.json"
        with open(spaces_file, "w") as f:
            json.dump([p.model_dump() for p in hf_spaces], f, indent=2, default=str)
        logger.info(f"Saved {len(hf_spaces)} HuggingFace spaces to {spaces_file}")


def main():
    """Main execution function."""
    # Setup paths first
    project_root = Path(__file__).parent.parent
    log_file = project_root / "indexing.log"

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(),
        ],
    )

    logger.info("=" * 60)
    logger.info("Starting project indexing")
    logger.info("=" * 60)

    # Load environment variables from parent directory
    env_path = project_root / ".env"
    load_dotenv(env_path)

    # Setup output paths (relative to project root)
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)

    output_file = data_dir / "project_index.json"
    organized_dir = data_dir / "organized"

    # Initialize indexers
    try:
        github_indexer = GitHubIndexer()
        logger.info("GitHub indexer initialized")
    except Exception as e:
        logger.error(f"Failed to initialize GitHub indexer: {e}")
        github_indexer = None

    try:
        hf_indexer = HuggingFaceIndexer()
        logger.info("HuggingFace indexer initialized")
    except Exception as e:
        logger.error(f"Failed to initialize HuggingFace indexer: {e}")
        hf_indexer = None

    if not github_indexer and not hf_indexer:
        logger.error("No indexers could be initialized. Exiting.")
        return

    # Load existing index or create new one
    index = load_existing_index(output_file)
    if index:
        logger.info("Using existing index for incremental update")
    else:
        logger.info("Creating new index")
        index = ProjectIndex()

    # Fetch GitHub projects
    if github_indexer:
        # Fetch repositories
        try:
            logger.info("Fetching GitHub repositories...")
            github_repos = github_indexer.fetch_public_repos()
            merge_stats = index.merge_projects(github_repos)
            logger.info(
                f"GitHub Repositories: {merge_stats['added']} added, "
                f"{merge_stats['updated']} updated"
            )
        except Exception as e:
            logger.error(f"Error fetching GitHub repositories: {e}")

        # Fetch gists
        try:
            logger.info("Fetching GitHub gists...")
            github_gists = github_indexer.fetch_public_gists()
            merge_stats = index.merge_projects(github_gists)
            logger.info(
                f"GitHub Gists: {merge_stats['added']} added, "
                f"{merge_stats['updated']} updated"
            )
        except Exception as e:
            logger.error(f"Error fetching GitHub gists: {e}")

        # Check rate limit
        try:
            rate_limit = github_indexer.check_rate_limit()
            remaining = rate_limit["rate"]["remaining"]
            logger.info(f"GitHub API rate limit remaining: {remaining}")
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")

    # Fetch HuggingFace projects
    if hf_indexer:
        try:
            logger.info("Fetching HuggingFace resources...")
            hf_projects = hf_indexer.fetch_all()
            merge_stats = index.merge_projects(hf_projects)
            logger.info(
                f"HuggingFace: {merge_stats['added']} added, "
                f"{merge_stats['updated']} updated"
            )
        except Exception as e:
            logger.error(f"Error fetching HuggingFace projects: {e}")

    # Sort by date (most recent first)
    index.sort_by_date(reverse=True)

    # Save unified index
    save_index(index, output_file)

    # Create organized output
    create_organized_output(index, organized_dir)

    logger.info("=" * 60)
    logger.info("Indexing complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
