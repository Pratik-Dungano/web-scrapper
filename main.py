"""
main.py
Entry point for the web scraper. Orchestrates input, extraction, and output.
"""
from scraper import input, extract, output, errors, utils

def main():
    """
    Main function to run the web scraper:
    1. Parse user input (search query or URLs)
    2. Validate and check reachability of URLs
    3. Fetch and extract company info
    4. Output results to CSV/JSON
    5. Handle and log errors
    """
    try:
        user_input = input.parse_args()
        if isinstance(user_input, str):
            # If a search query is provided, inform user and exit (no search implemented)
            utils.log_error("Search query input is not yet supported. Please provide URLs with --urls.")
            return
        urls = input.validate_urls(user_input)
        reachable_urls = input.check_reachability(urls)
        if not reachable_urls:
            utils.log_error("No reachable URLs provided.")
            return
        results = extract.process_urls(reachable_urls)
        if not results:
            utils.log_error("No company information could be extracted from the provided URLs.")
            return
        output.write_csv(results, "output.csv")
        output.write_json(results, "output.json")
        print(f"Extraction complete. {len(results)} records saved to output.csv and output.json.")
    except errors.InvalidURLError as e:
        utils.log_error(f"Invalid URL: {e}")
    except errors.URLUnreachableError as e:
        utils.log_error(f"Unreachable URL: {e}")
    except Exception as e:
        utils.log_error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
