# Import Section
import concurrent.futures
import urllib.parse
import requests
import hashlib
import json
import time
import re
import os
import lib_logger
import lib_authentication

# Global Variables

#########################################################
# VARIABLES FOR ALLOW LISTS
# API_KEY: Your NextDNS API key for authentication
API_KEY = lib_authentication.NEXTDNS_API_KEY

# PROFILE_ID: Your NextDNS Profile ID
PROFILE_ID = lib_authentication.NEXTDNS_PROFILE_ID

# ENDPOINT_URL_ALLOWLIST: The API endpoint URL for submitting allowed domains to NextDNS
ENDPOINT_URL_ALLOWLIST = 'https://api.nextdns.io/profiles/{}/allowlist'.format(PROFILE_ID)

# SOURCE_FILE_ALLOWED_DOMAINS: The source file containing explicitly allowed domains
SOURCE_FILE_ALLOWED_DOMAINS = '00allowdomains.txt'

# SOURCE_FILE_ALLOWED_LISTS: The source file containing URLs of allowed domain lists
SOURCE_FILE_ALLOWED_LISTS = '01allowlists.txt'

# OUTPUT_FILE_ALLOWED: The output file for the merged list of allowed domains
OUTPUT_FILE_ALLOWED = 'merged_allowed_domains.txt'

# TEMP_DIR_ALLOWED_LISTS: The temporary directory to store downloaded allowed domain lists
TEMP_DIR_ALLOWED_LISTS = 'temp_allowlists'

#########################################################
# VARIABLES FOR BLOCKLISTS

# ENDPOINT_URL_DENYLIST: The API endpoint URL for submitting blocked domains to NextDNS
ENDPOINT_URL_DENYLIST = 'https://api.nextdns.io/profiles/{}/denylist'.format(PROFILE_ID)

# SOURCE_FILE_BLOCKED_DOMAINS: The source file containing explicitly blocked domains
SOURCE_FILE_BLOCKED_DOMAINS = '00blockdomains.txt'

# SOURCE_FILE_BLOCKED_LISTS: The source file containing URLs of blocked domain lists
SOURCE_FILE_BLOCKED_LISTS = '01blocklists.txt'

# OUTPUT_FILE_BLOCKED: The output file for the merged list of blocked domains
OUTPUT_FILE_BLOCKED = 'merged_blocked_domains.txt'

# TEMP_DIR_BLOCKED_LISTS: The temporary directory to store downloaded blocked domain lists
TEMP_DIR_BLOCKED_LISTS = 'temp_blocklists'

# BATCH_SIZE: The number of domains to process in each batch when submitting to NextDNS
BATCH_SIZE = 1000

# MAX_THREADS: The maximum number of threads to use for concurrent domain submission
MAX_THREADS = 5

# MAX_RETRIES: The maximum number of retries for submitting a domain to NextDNS
MAX_RETRIES = 5

# domain_pattern: A compiled regular expression used for domain validation.
# It captures valid domains and subdomains, allowing for various TLD lengths and optional 'www' prefixes.
domain_pattern = re.compile(r'\b(?:www\.)?(([a-zA-Z0-9*]+(?:[-]*[a-zA-Z0-9*]+)*\.)+[a-zA-Z0-9]{2,63})\b')

def main():
    """
    The main function that orchestrates the entire flow of the program.
    It performs the following tasks:
    1. Sets up the logger for logging events and issues.
    2. Extracts and downloads allow and block lists from source files.
    3. Merges the downloaded lists into a single file.
    4. Cleans up and filters out irrelevant data from the merged lists.
    5. Submits the final list of domains to nextDNS.
    """

    # Step 1: Setup the logger
    lib_logger.setup_logger()

    # Step 2.1: Extract URLs of blocklists
    allowlist_urls = extract_list_urls(SOURCE_FILE_ALLOWED_LISTS)

    # Step 2.2: Download blocklists to a temporary directory
    download_domainlists(allowlist_urls, TEMP_DIR_ALLOWED_LISTS)

    # Step 2.3: Merge blocklist files into a single file
    merge_domainslist_files(TEMP_DIR_ALLOWED_LISTS, OUTPUT_FILE_ALLOWED)

    # Step 2.4: Clean up and replace the domains file
    clean_and_replace_domains_file(TEMP_DIR_ALLOWED_LISTS, OUTPUT_FILE_ALLOWED)

    # Step 2.5: Submit the compiled list of domains to NextDNS using multiple threads
    submit_domains_concurrently(OUTPUT_FILE_ALLOWED, MAX_THREADS, ENDPOINT_URL_ALLOWLIST)

    # Step 3.1: Extract URLs of blocklists
    blocklist_urls = extract_list_urls(SOURCE_FILE_BLOCKED_LISTS)

    # Step 3.2: Download blocklists to a temporary directory
    download_domainlists(blocklist_urls, TEMP_DIR_BLOCKED_LISTS)

    # Step 3.3: Merge blocklist files into a single file
    merge_domainslist_files(TEMP_DIR_BLOCKED_LISTS, OUTPUT_FILE_BLOCKED)

    # Step 3.4: Clean up and replace the domains file
    clean_and_replace_domains_file(TEMP_DIR_BLOCKED_LISTS, OUTPUT_FILE_BLOCKED)

    # Step 3.5: Submit the compiled list of domains to NextDNS using multiple threads
    submit_domains_concurrently(OUTPUT_FILE_BLOCKED, MAX_THREADS, ENDPOINT_URL_DENYLIST)


def extract_list_urls(SOURCE_FILE_LISTS):
    """
    Extracts URLs from the provided source file.

    Parameters:
    - SOURCE_FILE_LISTS (str): The path to the file containing the URLs.

    Returns:
    - list: A list of URLs extracted from the source file.

    The function reads each line of the file, strips it, and checks if it starts with "https://".
    If it does, the line (URL) is added to the list of URLs.
    """

    lib_logger.log_info(f'Starting Extraction of List Urls [{SOURCE_FILE_LISTS}]')

    urls = []
    with open(SOURCE_FILE_LISTS, 'r') as file:
        for line in file:
            stripped_line = line.strip()
            # Only process lines that start with "https://"
            if stripped_line.startswith("https://"):
                urls.append(stripped_line)
    return urls


def download_domainlists(LIST_URLS, TEMP_DIR):
    """
    Downloads domain lists from the provided URLs and saves them in a temporary directory.

    Parameters:
    - LIST_URLS (list): A list of URLs to download the domain lists from.
    - TEMP_DIR (str): The path to the temporary directory to save downloaded lists.

    The function iterates over each URL, downloads the content, and saves it in a file in the temporary directory.
    The filename is a hash of the URL to ensure uniqueness.
    """

    lib_logger.log_info(f'Started downloading Lists Files [{TEMP_DIR}]')

    # Create the download directory if it doesn't exist
    os.makedirs(TEMP_DIR, exist_ok=True)

    # Download each blocklist and save it as a file
    for url in LIST_URLS:
        # Create a safe filename for the blocklist using a hash of the URL
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        filename = os.path.join(TEMP_DIR, f"{url_hash}.txt")

        try:
            response = requests.get(url)
            response.raise_for_status()  # Check if the request was successful

            # Save the content of the response as a file
            with open(filename, 'wb') as file:
                file.write(response.content)

            lib_logger.log_info(f'Downloaded list from {url}')
        except requests.RequestException as e:
            lib_logger.log_error(f'Failed to download list from {url}: {e}')

    lib_logger.log_info('Finished downloading lists')


def merge_domainslist_files(TEMP_DIR, OUTPUT_FILE_NAME):
    """
    Merges multiple domain list files into a single output file.

    Parameters:
    - TEMP_DIR (str): The path to the temporary directory containing the domain list files.
    - OUTPUT_FILE_NAME (str): The name of the output file to save the merged content.

    The function iterates through each file in the temporary directory and appends its content to the output file.
    """

    lib_logger.log_info(f'Started List Files [{OUTPUT_FILE_NAME}]')

    # Create the output file
    with open(OUTPUT_FILE_NAME, 'w', encoding='utf-8') as output_file:
        for file_name in os.listdir(TEMP_DIR):
            file_path = os.path.join(TEMP_DIR, file_name)
            with open(file_path, 'r', encoding='utf-8') as input_file:
                # Read the contents of the input file and write them to the output file
                output_file.write(input_file.read())

    lib_logger.log_info('Finished Merging List Files')


def clean_up_line(line):
    """
    Cleans up a single line from a domain list file.

    Parameters:
    - line (str): The line to clean up.

    Returns:
    - str: A cleaned-up line containing only valid domains or subdomains, or None if the line should be skipped.

    The function performs the following:
    1. Strips leading and trailing whitespaces.
    2. Checks for empty or comment lines and skips them.
    3. Filters out invalid domains or subdomains.
    """

    # Remove leading and trailing whitespace, including newlines
    line = line.strip()
    lib_logger.log_info(f'Started Cleaning Up line [{line}]')

    # Check if the line is empty after stripping whitespace
    if not line:
        lib_logger.log_info("Skipped - Empty Line")
        return None

    # Check if the line starts with # or //
    if line.startswith('#') or line.startswith('//'):
        lib_logger.log_info("Skipped - Comment or Remark Line")
        return None

    # Split the line into individual entries using spaces as the delimiter
    entries = line.split()

    # Initialize a list to store valid entries (domains or subdomains)
    valid_entries = []

    for entry in entries:
        # Check if the entry matches the domain pattern
        match = re.search(domain_pattern, entry)
        if match:
            # If it's a valid domain or subdomain, add it to the list
            domain = match.group(1)  # Assuming the regex pattern has one capturing group
            valid_entries.append(domain)

    # Join the valid entries back into a line
    cleaned_line = " ".join(valid_entries)

    if cleaned_line:
        lib_logger.log_info(f"Cleaned - Domain Found! [{cleaned_line}]")
        return cleaned_line
    else:
        # If no valid entries are found, return None
        lib_logger.log_info("Skipped - No domains there")
        return None


def clean_and_replace_domains_file(TEMP_DIR_PATH, OUTPUT_FILE_NAME):
    """
    Cleans up and replaces the merged domains file.

    Parameters:
    - TEMP_DIR_PATH (str): The path to the temporary directory.
    - OUTPUT_FILE_NAME (str): The name of the output file to be cleaned and replaced.

    The function reads each line of the output file, cleans it using 'clean_up_line', and writes the cleaned lines to a temporary file.
    Finally, it replaces the original file with the cleaned-up version.
    """

    lib_logger.log_info(f'Started Cleaning the merged_domains file [{OUTPUT_FILE_NAME}]')

    input_file_path = OUTPUT_FILE_NAME  # Use the global OUTPUT_FILE_NAME variable as the input file
    temp_output_file_path = os.path.join(TEMP_DIR_PATH,
                                         'temp_' + OUTPUT_FILE_NAME)  # Construct the temp output file path

    # Create an empty temp output file
    with open(temp_output_file_path, 'w', encoding='utf-8') as temp_output_file:
        pass  # This will create an empty temp output file

    # Open the input file for reading and the temp output file for appending
    with open(input_file_path, 'r', encoding='utf-8') as input_file, \
            open(temp_output_file_path, 'a', encoding='utf-8') as temp_output_file:
        # Iterate through each line in the input file
        for line in input_file:
            # Clean up the line using the clean_up_line function
            cleaned_line = clean_up_line(line)

            # If the cleaned_line is not None (i.e., it's not empty or a comment), write it to the temp output file
            if cleaned_line is not None:
                temp_output_file.write(cleaned_line + '\n')

    # Replace the original file with the temp file
    os.replace(temp_output_file_path, input_file_path)


def submit_domains_concurrently(OUTPUT_FILE_NAME, BATCH_SIZE, ENDPOINT_URL):
    """
    Submits domains to NextDNS concurrently in batches.

    Parameters:
    - OUTPUT_FILE_NAME (str): The name of the file containing the domains to submit.
    - BATCH_SIZE (int): The number of domains to submit in each batch.
    - ENDPOINT_URL (str): The NextDNS API endpoint to submit the domains to.

    The function reads the domains from the output file and submits them to NextDNS in batches.
    It uses a ThreadPoolExecutor to perform the submissions concurrently.
    """

    lib_logger.log_info(f'Started submitting domains to NextDNS [{OUTPUT_FILE_NAME}]')

    # Read the compiled list of domains
    with open(OUTPUT_FILE_NAME, 'r', encoding='utf-8') as file:
        domains = file.read().splitlines()

    # Prepare the headers for the API request
    headers = {
        'X-Api-Key': API_KEY,
        'Content-Type': 'application/json'
    }

    def submit_domain(domain):
        retry_count = 0
        while retry_count < MAX_RETRIES:
            try:
                # Log the domain being submitted
                lib_logger.log_debug(f"[{domain}] Submitting domain")

                # Make the POST request to add the domain to the Denylist
                data = {'id': domain, 'active': True}
                response = requests.post(ENDPOINT_URL, json=data, headers=headers)
                response.raise_for_status()  # Check if the request was successful

                # Check if the response is not empty before trying to parse it as JSON
                if response.text:
                    lib_logger.log_info(f"[{domain}] Response: {response.text}")
                    lib_logger.log_info(f"[{domain}] Domain submitted successfully")
                else:
                    lib_logger.log_warning(f"[{domain}] Empty response received")
                break  # Break the loop on success
            except requests.RequestException as e:
                if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 429:
                    retry_count += 1
                    lib_logger.log_warning(f"[{domain}] Retry #{retry_count} after encountering 429 error")
                    time.sleep(5)  # Wait for a few seconds before retrying (adjust as needed)
                else:
                    lib_logger.log_error(f"[{domain}] Error Submitting: {e}")
                    break  # Break the loop on other errors

        if retry_count == MAX_RETRIES:
            lib_logger.log_error(f"[{domain}] Max retries reached. Giving up.")

    # Split domains into batches
    for i in range(0, len(domains), BATCH_SIZE):
        batch = domains[i:i + BATCH_SIZE]

        # Create a ThreadPoolExecutor to submit domains concurrently in this batch
        with concurrent.futures.ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:
            # Log when the threads start for this batch
            lib_logger.log_debug(f'Starting batch {i // BATCH_SIZE + 1} of {BATCH_SIZE} threads for domain submission')

            # Submit domains in this batch concurrently
            executor.map(submit_domain, batch)

        # Wait for 1 second before the next batch
        time.sleep(1)

    lib_logger.log_info('Finished submitting domains to NextDNS')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
