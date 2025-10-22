# Development Project Index

A unified data source for your code projects across GitHub and Hugging Face platforms. This tool incrementally pulls and organizes project data into a structured JSON format.

## Features

- **Multi-Platform Support**: Indexes projects from both GitHub and Hugging Face
- **Comprehensive Coverage**: Captures repositories, spaces, datasets, and models
- **Incremental Updates**: Efficiently updates existing data without duplication
- **Organized Output**: Generates both unified and categorized JSON files
- **Public Projects Only**: Automatically filters out private repositories and resources
- **Rich Metadata**: Includes creation dates, descriptions, stars, topics, and more

## Project Structure

```
Development-Project-Index/
├── index_projects.py        # Main indexing script
├── schema.py                # Data models and schema definitions
├── github_indexer.py        # GitHub API integration
├── huggingface_indexer.py   # Hugging Face API integration
├── requirements.txt         # Python dependencies
├── .env                     # API credentials (not committed)
├── project_index.json       # Unified output (generated)
├── organized_output/        # Categorized outputs (generated)
│   ├── github_repositories.json
│   ├── huggingface_models.json
│   ├── huggingface_datasets.json
│   └── huggingface_spaces.json
└── indexing.log            # Execution logs (generated)
```

## Setup

### Prerequisites

- Python 3.8+
- GitHub Personal Access Token
- Hugging Face API Token

### Installation

1. Clone the repository:
```bash
cd ~/repos/github/Development-Project-Index
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API credentials in `.env`:
```env
GITHUB_API_KEY="your_github_token_here"
HF_CLI="your_huggingface_token_here"
```

**Note**: The `.env` file is gitignored to protect your credentials.

### Getting API Tokens

**GitHub Personal Access Token:**
1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Generate new token with `repo` and `user` scopes
3. Copy the token to your `.env` file

**Hugging Face Token:**
1. Go to https://huggingface.co/settings/tokens
2. Create a new token with read permissions
3. Copy the token to your `.env` file

## Usage

### Basic Execution

Run the indexing script:

```bash
python index_projects.py
```

Or make it executable and run directly:

```bash
chmod +x index_projects.py
./index_projects.py
```

### Incremental Updates

The script automatically performs incremental updates:
- **First run**: Creates a new index with all public projects
- **Subsequent runs**: Loads existing data and merges new/updated projects
- **Smart merging**: Adds new projects and updates existing ones based on `source:full_name` keys

### Output Files

**Unified Index** (`project_index.json`):
- Contains all projects from all sources in a single file
- Includes metadata about the index (generation time, counts by source/type)
- Projects sorted by creation date (most recent first)

**Organized Outputs** (`organized_output/`):
- Separate JSON files for each project type
- Easier to work with specific categories
- Same data structure as unified index

## Data Schema

Each project in the index contains:

```json
{
  "source": "GitHub | HuggingFace",
  "type": "Repository | Model | Dataset | Space",
  "name": "project-name",
  "full_name": "username/project-name",
  "description": "Project description",
  "url": "https://...",
  "created_at": "2024-01-01T00:00:00+00:00",
  "updated_at": "2024-01-02T00:00:00+00:00",
  "language": "Python",
  "stars": 42,
  "topics": ["machine-learning", "nlp"]
}
```

## Project Types

### GitHub
- **Repository**: Public code repositories

### Hugging Face
- **Model**: Public machine learning models
- **Dataset**: Public datasets
- **Space**: Public Gradio/Streamlit applications

## Logging

Execution logs are written to:
- `indexing.log` - Detailed logs of all operations
- Console output - Real-time progress and statistics

## Error Handling

The script includes comprehensive error handling:
- Gracefully handles missing API keys
- Continues indexing even if one source fails
- Logs errors without stopping execution
- Reports API rate limits for GitHub

## Automation

### Scheduled Updates

You can automate the indexing with cron:

```bash
# Run daily at 2 AM
0 2 * * * cd /home/daniel/repos/github/Development-Project-Index && /usr/bin/python3 index_projects.py >> cron.log 2>&1
```

### Version Control

Consider version controlling the output:

```bash
git add project_index.json organized_output/
git commit -m "Update project index"
git push
```

## Privacy & Security

- Only public projects are indexed
- Private repositories/resources are explicitly filtered out
- API tokens are stored in `.env` (gitignored)
- No sensitive data is included in outputs

## Performance

- **GitHub**: Uses pagination to handle large numbers of repositories
- **HuggingFace**: Fetches up to 500 items per type
- **Rate Limits**: Monitors GitHub API rate limits
- **Incremental**: Only processes changed data on subsequent runs

## Troubleshooting

### API Authentication Issues

If you see authentication errors:
1. Verify tokens in `.env` are correct
2. Check token permissions/scopes
3. Ensure tokens haven't expired

### Missing Projects

If some projects don't appear:
1. Verify they are public (not private)
2. Check the logs for API errors
3. Ensure you have the latest token permissions

### Rate Limiting

GitHub has rate limits (5000 requests/hour for authenticated users):
- The script checks remaining rate limit
- Logs show current limit status
- Consider spacing out frequent runs

## Contributing

This is a personal project indexer, but improvements are welcome:
- Better error handling
- Additional platforms (GitLab, Bitbucket, etc.)
- Performance optimizations
- Enhanced filtering options

## License

Personal project - see repository settings for license information.
