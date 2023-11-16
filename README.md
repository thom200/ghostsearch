# ghostsearch
#This tool search for website subdomains using SecurityTrails and search the domain on Censys to get related machines ip with misconfigured
#after found ips the script check if port 80 and 443 port is open and do a search on "dirsearch" to find sensitive archives or directory

1. Create Censys and SecurityTrails account.
2. Get the keys and add on ghostsearch code.
3. install dirsearch sudo apt-get install dirsearch.
4. python3 ghostsearch.py
