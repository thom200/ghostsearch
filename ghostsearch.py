import requests
import subprocess
from tabulate import tabulate
from termcolor import colored

# Configuration of API keys (please set these environment variables or prompt for them)
CENSYS_API_ID = ''  # Set your Censys API ID or prompt for it
CENSYS_SECRET = ''  # Set your Censys Secret or prompt for it
SECURITYTRAILS_API_KEY = ''  # Set your SecurityTrails API Key or prompt for it

def print_info(message):
    print("\033[94m[*]\033[0m " + message)  # Blue

def print_success(message):
    print("\033[92m[+]\033[0m " + message)  # Green

def print_error(message):
    print("\033[91m[-]\033[0m " + message)  # Red

def print_table(headers, data):
    print(tabulate(data, headers=headers, tablefmt="grid"))

# Function to get subdomains from SecurityTrails
def get_subdomains(domain):
    url = f"https://api.securitytrails.com/v1/domain/{domain}/subdomains"
    headers = {'APIKEY': SECURITYTRAILS_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        subdomains_data = response.json()
        subdomains = subdomains_data.get('subdomains', [])
        return [f"{sub}.{domain}" for sub in subdomains]
    except requests.RequestException as e:
        print_error(f"Error obtaining subdomains: {e}")
        return []

# Function to search the main domain in Censys and obtain IPs
def search_censys(domain):
    url = "https://search.censys.io/api/v2/hosts/search"
    auth = (CENSYS_API_ID, CENSYS_SECRET)
    params = {'q': domain}
    try:
        response = requests.get(url, auth=auth, params=params)
        response.raise_for_status()
        results = response.json().get('result', {}).get('hits', [])
        ips = [result.get('ip') for result in results if result.get('ip')]
        return ips
    except requests.RequestException as e:
        print_error(f"Error searching in Censys: {e}")
        return []

# Function to check if dirsearch is installed
def is_dirsearch_installed():
    try:
        subprocess.run(["dirsearch", "-h"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("dirsearch is not installed or not in the PATH.")
        return False

# Function to run dirsearch
def run_dirsearch(ip, protocol):
    url = f"{protocol}://{ip}"
    print_info(f"Running dirsearch on {url}")
    try:
        subprocess.run(['dirsearch', '-u', url, '-e', 'php,pht,bkp,example,txt,js,json,config,backup,sql,html,bd,config'], check=True)
    except subprocess.CalledProcessError as e:
        print_error(f"dirsearch failed for {url}: {e}")

# Main script
if __name__ == "__main__":
    if is_dirsearch_installed():
        domain = input("Enter a domain (e.g., google.com): ")
        print_info(f"Searching for subdomains for {domain}...")
        subdomains = get_subdomains(domain)
        if subdomains:
            print_table(["Subdomains"], [[sd] for sd in subdomains])
            print_success(f"{len(subdomains)} subdomains found.")
        else:
            print_error("No subdomains found.")

        print_info(f"Searching for IPs for {domain} on Censys...")
        ips = search_censys(domain)
        if ips:
            print_table(["IPs"], [[ip] for ip in ips])
            print_success(f"{len(ips)} IPs found.")
            for ip in ips:
                for protocol in ['http', 'https']:
                    run_dirsearch(ip, protocol)
        else:
            print_error(f"No IPs found for {domain}.")
    else:
        print_error("Please install dirsearch before running this script.")
