# AI Job Search Agent

An automated job search tool that scans multiple job boards daily for AI-related positions.

## Why I Built This

I built this to demonstrate automation skills and optimize my own job search. The agent scans 50+ company career pages daily and can be configured for any role type - just edit the keywords in the config file.

## Features

- **Multi-board Search**: Automatically scans Greenhouse, Lever, and other job platforms
- **Smart Filtering**: Matches jobs based on customizable keywords and criteria
- **Daily Reports**: Generates clean, readable summaries of new postings
- **Data Export**: Saves results in both JSON (for processing) and TXT (for reading)
- **Extensible**: Easy to add new job boards or customize search criteria

## Quick Start

### Requirements

- Python 3.10 or higher
- pip (Python package manager)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/ai-job-search-agent.git
cd ai-job-search-agent
```

2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

3. Run the agent:
```bash
python3 job_search_agent.py
```

## What It Searches For

The agent currently searches for these types of roles:

- Prompt Engineer
- AI Content Writer/Strategist
- Content Engineer
- AI UX Designer/Researcher
- AI Product Designer

You can customize these in `config.json`.

## Customization

Edit `config.json` to customize your search:
```json
{
  "job_titles": ["Your preferred job titles"],
  "keywords": ["prompt engineer", "ai ux"],
  "greenhouse_companies": ["anthropic", "openai"],
  "lever_companies": ["netflix", "stripe"]
}
```

## Output

The agent generates two files:

- `job_results_[timestamp].json` - Structured data for further processing
- `job_results_[timestamp].txt` - Human-readable report

## Automation

### Run Daily with Cron (Mac/Linux)

Add to your crontab:
```bash
0 9 * * * cd /path/to/job-search-agent && python job_search_agent.py
```

### GitHub Actions

For automated daily searches on GitHub:

1. Fork this repo
2. Enable GitHub Actions
3. The agent will run daily (see `.github/workflows/daily-search.yml`)

## Technical Details

Built with:
- Python 3
- requests - HTTP library
- BeautifulSoup4 - HTML parsing

## Roadmap

- Add LinkedIn job search
- Email notifications
- Duplicate detection
- Salary filtering
- Application tracking

## License

MIT License - feel free to use this for your own job search

## Tips

1. Run this daily - new jobs get posted constantly
2. Apply early - first applicants get more attention
3. Customize your search - edit config.json to match your preferences
4. Track your applications - use the JSON output to build a tracker


