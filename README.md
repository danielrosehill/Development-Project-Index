# Development Project Index

A personal tool for indexing my public projects across GitHub and Hugging Face platforms. This repository serves as both my project index and an open-source pattern that others can adapt for their own use.

## About This Tool

This is my personal project indexer that I use to maintain a unified view of all my public work. The code is open source so you can fork it and adapt the pattern for your own project indexing needs.

## Index Data Files

### Main Index
- **[Complete Project Index](data/project_index.json)** - All 723 projects in one unified file

### By Platform & Type

**GitHub (655 projects)**
- [Repositories](data/organized/github_repositories.json) - 528 public repos
- [Gists](data/organized/github_gists.json) - 127 public gists

**Hugging Face (68 projects)**
- [Datasets](data/organized/huggingface_datasets.json) - 42 datasets
- [Spaces](data/organized/huggingface_spaces.json) - 26 spaces

---

## What It Does

- **Indexes projects** from GitHub (repos, gists) and Hugging Face (datasets, spaces)
- **Incremental updates**: Efficiently merges new/updated projects without duplication
- **Organized outputs**: Both unified and categorized JSON files
- **Public only**: Automatically filters out private resources
- **Rich metadata**: Creation dates, descriptions, languages, topics, and more

## Project Structure

```
Development-Project-Index/
├── src/                        # Source code
│   ├── index_projects.py       # Main indexing script
│   ├── schema.py               # Data models
│   ├── github_indexer.py       # GitHub API integration
│   ├── huggingface_indexer.py  # Hugging Face API integration
│   └── requirements.txt        # Python dependencies
├── data/                       # Generated data (committed)
│   ├── project_index.json      # Unified index
│   └── organized/              # Categorized outputs
│       ├── github_repositories.json
│       ├── github_gists.json
│       ├── huggingface_datasets.json
│       └── huggingface_spaces.json
├── .env                        # API credentials (gitignored)
├── update_index.sh             # Convenient update script
└── README.md                   # This file
```

## Using This Pattern For Your Own Projects

If you want to create your own project index using this pattern:

### Prerequisites

- Python 3.8+
- GitHub Personal Access Token
- Hugging Face API Token (if you use HF)

### Setup

1. Fork or clone this repository:
```bash
git clone https://github.com/danielrosehill/Development-Project-Index.git
cd Development-Project-Index
```

2. Create virtual environment and install dependencies:
```bash
uv venv
uv pip install -r src/requirements.txt
```

3. Configure your API credentials in `.env`:
```env
GITHUB_API_KEY="your_github_token_here"
HF_CLI="your_huggingface_token_here"
```

### Getting API Tokens

**GitHub Personal Access Token:**
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token with `repo` and `user` scopes
3. Copy the token to your `.env` file

**Hugging Face Token:**
1. Go to https://huggingface.co/settings/tokens
2. Create a new token with read permissions
3. Copy the token to your `.env` file

## Usage

### Running the Indexer

Use the convenient update script:

```bash
./update_index.sh
```

Or run directly:

```bash
source .venv/bin/activate
python src/index_projects.py
```

### Incremental Updates

The script automatically performs incremental updates:
- **First run**: Creates a new index with all public projects
- **Subsequent runs**: Loads existing data and merges new/updated projects
- **Smart merging**: Updates existing projects based on `source:full_name` keys

### Output Files

The script generates two types of output:

**Main Index** ([data/project_index.json](data/project_index.json)):
- All projects in one file with metadata and counts
- Projects sorted by creation date (most recent first)

**By Type** ([data/organized/](data/organized/)):
- Separate JSON files for each project type
- Same data structure, easier to work with specific categories

## Data Schema

Each project includes:
- Source (GitHub/HuggingFace) and type (Repository/Gist/Dataset/Space)
- Name, description, and URL
- Creation and update timestamps
- Language and topics (where applicable)

## Technical Details

- **Incremental updates**: Only processes changed data on subsequent runs
- **Public only**: Private repositories/resources are filtered out
- **Rate limits**: Monitors GitHub API rate limits
- **Logging**: Detailed logs written to `indexing.log`
- **Security**: API tokens stored in `.env` (gitignored)

## License

MIT License - See LICENSE file for details

## Contact

Daniel Rosehill
[GitHub](https://github.com/danielrosehill) | [Hugging Face](https://huggingface.co/danielrosehill)
