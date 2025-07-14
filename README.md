# Web Scraper Assignment

## Project Overview
This project is a robust, modular Python web scraping tool designed to extract and enrich company information from the web. It is built to meet and exceed the requirements of a typical web scraping assignment, supporting both minimal and advanced features. The tool is production-grade, extensible, and easy to use.

## What Does This Project Do?
- **Accepts a list of website URLs** from the user via command-line arguments or a web dashboard.
- **Validates and checks** each URL for proper formatting and reachability.
- **Fetches web pages** and parses their HTML content.
- **Extracts company information** at multiple levels:
  - **Level 1 (Basic):** Company name, website URL, email, phone.
  - **Level 2 (Medium):** Social media profiles (LinkedIn, Twitter, Facebook, Instagram), address/location, company overview (description, tagline, year founded), products/services, industry/sector.
  - **Level 3 (Advanced):** Tech stack (detected technologies), current projects/focus areas, competitors, market positioning.
- **Enriches data** using the Hunter.io API:
  - Adds organization name, industry, emails, country, full state name, city, phone, LinkedIn, and more.
- **Outputs all data** in both CSV and JSON formats for easy analysis.
- **Handles errors gracefully** and logs them to both the console and a log file (`scraper_errors.log`).
- **Is modular and extensible** for future enhancements (dynamic content, pagination, etc.).

## Advanced Features & Improvements
- **Dynamic Content Handling:** Scrape JavaScript-rendered pages using Selenium. Enable with `--dynamic` or the dashboard checkbox.
- **Pagination & URL Discovery:** Automatically follows “Next”/pagination links to scrape multi-page listings. Enable with `--paginate` or the dashboard checkbox.
- **Proxy Support:** Rotate through a list of proxies for each request to avoid blocks and mimic human browsing. Provide a `proxies.txt` file and use `--proxies proxies.txt` or the dashboard field.
- **Custom Config File:** Use a YAML config file (e.g., `example_config.yaml`) to specify custom CSS selectors and regex for extraction. Enable with `--config example_config.yaml` or the dashboard field.
- **Web Dashboard:** User-friendly web interface (Flask) for submitting jobs, monitoring progress, and downloading results. Run with `python dashboard.py`.
- **Progress Bar & Summary:** Real-time CLI progress bar (tqdm) and summary statistics after each run.
- **Info Logging:** Logs both info and error messages to the console and `scraper_errors.log` for full traceability.
- **Flexible CLI:** All features can be controlled via command-line flags or the dashboard.
- **Example Files:** Includes `proxies.txt` and `example_config.yaml` for quick setup and customization.

## Features
- **Input Handling:** Accepts URLs via CLI or dashboard, validates and checks reachability.
- **Multi-Level Data Extraction:**
  - Level 1: Basic company info (name, URL, contact)
  - Level 2: Social, address, overview, products/services, industry
  - Level 3: Tech stack, projects, competitors, market position
- **API Enrichment:** Integrates with Hunter.io for richer, standardized company data.
- **Structured Output:** Saves results to `output.csv` and `output.json`.
- **Error Handling:** Logs errors to both the console and `scraper_errors.log`.
- **Modular Codebase:** Organized into input, extraction, output, error handling, and utility modules.
- **Web Dashboard:** Modern, Bootstrap-based UI for job management and monitoring.
- **Progress Bar:** Real-time feedback in the CLI.
- **Proxy & Config Support:** Easily adapt to any site or network environment.

## How It Meets Assignment Requirements
- **Minimal/Core Features:** Fully implemented (input, validation, extraction, output, error handling)
- **Optional/Advanced Features:** Implemented (multi-level extraction, enrichment, logging, dynamic content, pagination, proxy, config, dashboard)
- **Documentation:** This README provides a clear overview, feature list, and usage instructions.
- **Testing:** Test structure is present and can be expanded.

## Setup
1. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Unix/Mac:
   source venv/bin/activate
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage
- **CLI Example:**
  ```sh
  python main.py --urls https://example.com --dynamic --paginate --delay 2 5 --proxies proxies.txt --config example_config.yaml
  ```
- **Web Dashboard:**
  ```sh
  python dashboard.py
  # Then open http://127.0.0.1:5000/ in your browser
  ```
- Output will be saved as `output.csv` and `output.json` in the project directory.

## Output Sample
- The output files will contain all extracted and enriched fields for each company/URL.

## Error & Info Logging
- Errors and info messages are printed to the console and also saved in `scraper_errors.log` for review.

## Example Files
- `proxies.txt`: Example proxy list for rotating IPs.
- `example_config.yaml`: Example config for custom selectors/regex.

## Extending the Project
- The codebase is modular and ready for enhancements such as:
  - Further dynamic content handling (Playwright, Puppeteer)
  - More advanced crawling and scheduling
  - Additional API integrations
  - More automated tests

## License
This project is for educational and demonstration purposes.
