# Website Wordlist Scan

## Info
Multithreaded utility to scan a website using wordlists written in Python

## Install
Clone this repository
```
git clone https://github.com/ryzeon-dev/wws
```

Enter the directory
```
cd wws
```

Create and activate a Python virtual environment (Optional, Recommended)
```
python3 -m venv venv
source ./venv/bin/activate
```

Install the requirements using pip
```
python3 -m pip install -r requirements
```

## Usage
```
python3 wws.py --help
wws: Website Wordlist Scan
usage: wsws WEBSITE WORDLIST [OPTIONS]
notes:
    the website must contain the "HERE" placeholder, which tells the program where to put the words from the wordlist
    e.g.
        http://google.com/HERE   scans for pages
        http://HERE.google.com/  scans for subdomains

options:
    -a | --accept CODES       List of status codes to accept, comma separated (default is 200,201,202,203,204,205,206,207,208)
    -f | --follow             Follow redirects
    -h | --help               Show this message and exit
    -t | --threads THREADS    Number of parallel threads, default is 8
```
