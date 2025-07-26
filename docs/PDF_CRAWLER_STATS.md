# Crawl Stats PDF Report

## What it Does

- The `crawl_stats_pdf_service.py` script generates a PDF report with statistics about news crawling activity from the last 24 hours.
- It fetches crawl stats from the database and creates a table summarizing the results for each subscription.

## How it Works

1. **Fetch Crawl Stats**
   - Retrieves crawl statistics for the last day from the database.
2. **Generate PDF**
   - Builds a PDF with a title, date, and a table showing:
     - Subscription name
     - Total successful crawls
     - Total attempted crawls
     - Notes (if any)
   - The table is formatted for readability and fits all data on one page per subscription.
3. **Save PDF**
   - The PDF is saved as `crawl_stats_report.pdf` in the backend directory.

## Example

<div align="center">

### [View example crawl stats PDF report](example_crawl_stats_report.pdf)

</div>
