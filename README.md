# 🌐 nextDNS Domain Manager 🌐

## Introduction
Welcome to the nextDNS Domain Manager! This tool simplifies the complexities of managing multiple allow and block domain lists for nextDNS. Designed to be both efficient and user-friendly, it automates key tasks so you can focus on what really matters. Here's what it does:

- Reads domains from source files, including those you explicitly want to allow or block.
- Retrieves additional domains from external sources for a comprehensive list.
- Compiles all these domains into a single, clean file, eliminating any irrelevant data.
- Seamlessly submits this well-crafted list to your nextDNS profile's allowlist or denylist.

It's an all-in-one solution for those looking to streamline their nextDNS domain management. 🌐

## Installation

Setting up the nextDNS Domain Manager is a breeze. Just follow these simple steps:

### Prerequisites
- Python 3.x
- An API key from nextDNS
- Your nextDNS Profile ID

### Where to Find API Key and Profile ID
- **API Key**: Can be retrieved from [your nextDNS account](https://my.nextdns.io/account).
- **Profile ID**: Found on the Setup Page of the profile you wish to manage. Also visible in the URL tab of your browser, like `https://my.nextdns.io/{profile_id}/setup`.

For more details on how the API works, refer to the [official nextDNS API documentation](https://nextdns.io/api).

### Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/sacra2kx/nextdns-domain-manager.git
   ```
   
2. **Navigate to the Project Directory**
   ```bash
   cd nextDNS-Domain-Manager
   ```

3. **Install Required Libraries**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API Key and Profile ID**
   - Replace `API_KEY` with your own nextDNS API key in the script file.
   - Replace `PROFILE_ID` with your nextDNS Profile ID in the script file.

5. **Run the Script**
   ```bash
   python main.py
   ```

You're all set! Enjoy streamlined domain management with nextDNS.

## Usage

Using the nextDNS Domain Manager couldn't be easier. Here's how to make the most of it:

### For Allowlists

1. **Prepare Your Allowlist File**
   - Create a text file (`00allowdomains.txt`) and list the domains you want to allow, one per line.

2. **Prepare Your External Allowlist Sources**
   - Create another text file (`01allowlists.txt`) and list the URLs of external domain lists you'd like to include, one per line.

### For Blocklists

1. **Prepare Your Blocklist File**
   - Create a text file (`00blockdomains.txt`) and list the domains you want to block, one per line.

2. **Prepare Your External Blocklist Sources**
   - Create another text file (`01blocklists.txt`) and list the URLs of external domain lists you'd like to include, one per line.

### Running the Script

To process both allowlists and blocklists, simply run:

```bash
python main.py
```

## TODO 📋

Exciting updates are on the way:

1. **Implement Command-Line Options**
   - `--allow [allowlists_source] [allowdomains_source]`: Process `allowlists` and `allowdomains` from the specified or default source files.
   - `--allowlists [source_file]`: Process only the `allowlists` from the specified or default source files.
   - `--allowdomains [source_file]`: Process only the `allowdomains` from the specified or default source files.
   - `--removeallow "domain"`: Remove a specific domain from the allowlist.
   - `--clearallow`: Remove all domains from the allowlist.
   - `--block [blocklists_source] [blockdomains_source]`: Process `blocklists` and `blockdomains` from the specified or default source files.
   - `--blocklists [source_file]`: Process only the `blocklists` from the specified or default source files.
   - `--blockdomains [source_file]`: Process only the `blockdomains` from the specified or default source files.
   - `--removeblock "domain"`: Remove a specific domain from the blocklist.
   - `--clearblock`: Remove all domains from the blocklist.
   - `--submit yes/no/true/false/1/0`: Enable or disable nextDNS submission.

2. **Refine Logging**
   - Introduce a mechanism to set the log level at runtime.
   - Standardize logging format for easier troubleshooting.

3. **Performance Optimization**
   - Utilize multi-threading even more efficiently to speed up domain submission.

4. **Domain Removal Routine**
   - Create a routine to remove domains that aren't in the app-generated lists anymore.

5. **User Interface**
   - Develop a graphical user interface for an enhanced user experience.

6. **Documentation**
   - Comprehensive user manual and developer documentation.