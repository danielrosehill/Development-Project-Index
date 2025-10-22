"""
Schema definitions for the unified project index.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field


class Project(BaseModel):
    """Unified project model for all sources."""

    source: str = Field(..., description="Source platform: GitHub or HuggingFace")
    type: str = Field(..., description="Project type: Repo, Space, Dataset, Model")
    name: str = Field(..., description="Project name")
    full_name: str = Field(..., description="Full project identifier (e.g., username/repo)")
    description: Optional[str] = Field(None, description="Project description")
    url: str = Field(..., description="Direct link to the project")
    created_at: Optional[datetime] = Field(None, description="Creation date")
    updated_at: Optional[datetime] = Field(None, description="Last update date")
    language: Optional[str] = Field(None, description="Primary programming language")
    topics: List[str] = Field(default_factory=list, description="Tags/topics")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ProjectIndex(BaseModel):
    """Root model for the unified project index."""

    metadata: Dict[str, Any] = Field(
        default_factory=lambda: {
            "generated_at": datetime.now().isoformat(),
            "version": "1.0"
        }
    )
    projects: List[Project] = Field(default_factory=list)

    def add_project(self, project: Project) -> None:
        """Add a project to the index."""
        self.projects.append(project)

    def get_project_key(self, project: Project) -> str:
        """
        Generate a unique key for a project.

        Args:
            project: Project object.

        Returns:
            Unique string key (e.g., "GitHub:username/repo").
        """
        return f"{project.source}:{project.full_name}"

    def find_project(self, project: Project) -> Optional[Project]:
        """
        Find an existing project in the index.

        Args:
            project: Project to search for.

        Returns:
            Existing project if found, None otherwise.
        """
        key = self.get_project_key(project)
        for existing in self.projects:
            if self.get_project_key(existing) == key:
                return existing
        return None

    def merge_project(self, new_project: Project) -> bool:
        """
        Merge a project into the index (add or update).

        Args:
            new_project: Project to merge.

        Returns:
            True if project was added, False if updated.
        """
        existing = self.find_project(new_project)

        if existing:
            # Update existing project
            idx = self.projects.index(existing)
            self.projects[idx] = new_project
            return False
        else:
            # Add new project
            self.add_project(new_project)
            return True

    def merge_projects(self, new_projects: List[Project]) -> Dict[str, int]:
        """
        Merge multiple projects into the index.

        Args:
            new_projects: List of projects to merge.

        Returns:
            Dictionary with counts of added and updated projects.
        """
        added = 0
        updated = 0

        for project in new_projects:
            was_added = self.merge_project(project)
            if was_added:
                added += 1
            else:
                updated += 1

        return {"added": added, "updated": updated}

    def get_by_source(self, source: str) -> List[Project]:
        """Get all projects from a specific source."""
        return [p for p in self.projects if p.source == source]

    def get_by_type(self, project_type: str) -> List[Project]:
        """Get all projects of a specific type."""
        return [p for p in self.projects if p.type == project_type]

    def sort_by_date(self, reverse: bool = True) -> None:
        """Sort projects by creation date."""
        self.projects.sort(
            key=lambda x: x.created_at or datetime.min,
            reverse=reverse
        )

    def to_json(self) -> str:
        """Export index to JSON string."""
        return self.model_dump_json(indent=2)
