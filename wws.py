#!/usr/bin/python3

import requests 
from threading import Thread, Semaphore 
import time 

REJECT = []
ACCEPT = [200, 201, 202, 203, 204, 205, 206, 207, 208]
REDIRECTS = False

WORDS_COUNT = 0
CHECKED = 0

class Printer:
    def __init__(self):
        self.mutex = Semaphore(1)
        self.maxLen = 0

    def print(self, *args, **kwargs):
        self.mutex.acquire()
        
        text = ' '.join(args)

        if (end := kwargs.get('end')) == '':
            self.maxLen = max(len(text), self.maxLen)
            print(text + ' ' * (self.maxLen - len(text)), **kwargs)
        
        else:
            print(text.ljust(self.maxLen), **kwargs)

        self.mutex.release()

printer = Printer()

class Threadpool:
    def __init__(self, threads):
        self.threads = [None] * threads 
        self.size = threads 
        
        self.run = True
        self.queueMutex = Semaphore(1)
        self.queue = []
        
        self._makeThreads()

    def _makeThreads(self):
        for _ in range(self.size):
            self.threads.append(Thread(target=self._threadLoop, args=()))
            self.threads[-1].start()

    def _threadLoop(self):
        while self.run:
            if not self.queue:
                time.sleep(0.01)
                continue

            self.queueMutex.acquire()
            task, args = self.queue.pop(0)
            
            self.queueMutex.release()
            task(*args)
            

    def exec(self, fn, args):
        self.queueMutex.acquire()
        self.queue.append((fn, args))
        self.queueMutex.release()

    def killAll(self):
        self.run = False

        for thread in self.threads:
            if thread is not None:
                thread.join()

def check(domain, target):
    global printer, CHECKED, REJECT, ACCEPT, REDIRECTS
    
    url = domain.replace('HERE', target)
    CHECKED += 1
    printer.print(f'\r[{CHECKED}/{WORDS_COUNT}] trying {url}', end='')

    try:
        response = requests.get(url, allow_redirects=REDIRECTS)
    
    except:
        return
    
    else:
        code = response.status_code
        if REJECT: 
            if code not in REJECT:
                printer.print(f'\r>> {url} -> code {code}')
        
        else:
            if code in ACCEPT:
                printer.print(f'\r>> {url} -> code {code}')
        

if __name__ == "__main__":
    import sys 
    args = sys.argv[1:]

    if '-h' in args or '--help' in args or not args:
        print('wws: Website Wordlist Scan')
        print('usage: wsws WEBSITE WORDLIST [OPTIONS]')
        print('notes:')
        print('    the website must contain the "HERE" placeholder, which tells the program where to put the words from the wordlist')
        print('    e.g.')
        print('        http://google.com/HERE   scans for pages')
        print('        http://HERE.google.com/  scans for subdomains')
        print('\noptions:')
        print('    -a | --accept CODES       List of status codes to accept, comma separated (default is 200,201,202,203,204,205,206,207,208)')
        print('    -f | --follow             Follow redirects')
        print('    -h | --help               Show this message and exit')
        print('    -r | --reject CODES       List of status codes to reject, comma separated; if specified, the accepted list is ignored')
        print('    -t | --threads THREADS    Number of parallel threads, default is 8')
        sys.exit(0)

    if '-f' in args:
        args.remove('-f')
        REDIRECTS = True

    elif '--follow' in args:
        args.remove('--follow')
        REDIRECTS = True
    
    if '-r' in args:
        index = args.index('-r')
        args.pop(index)

        try:
            REJECT = [int(code) for code in args.pop(index).split(',')]
        except:
            print('Error: rejected status codes must be integers comma separated')
            sys.exit(1)

    elif '--reject' in args:
        index = args.index('--reject')
        args.pop(index)

        try:
            REJECT = [int(code) for code in args.pop(index).split(',')]
        except:
            print('Error: rejected status codes must be integers comma separated')
            sys.exit(1)



    if '-a' in args:
        index = args.index('-a')
        args.pop(index)

        try:
            ACCEPT = [int(code) for code in args.pop(index).split(',')]

        except:
            print('Error: accepted status codes must be integers comma separated')
            sys.exit(1)

    elif '--accept' in args:
        index = args.index('--accept')
        args.pop(index)

        try:
            ACCEPT = [int(code) for code in args.pop(index).split(',')]

        except:
            print('Error: accepted status codes must be integers comma separated')
            sys.exit(1)

    if '-t' in args:
        index = args.index('-t')
        args.pop(index)

        try:
            threads = int(args.pop(index))
        
        except:
            print('Error: threads number must be an integer')
            sys.exit(1)

    elif '--threads' in args:
        index = args.index('--threads')
        args.pop(index)

        try:
            threads = int(args.pop(index))
        
        except:
            print('Error: threads number must be an integer')
            sys.exit(1)
    
    else:
        threads = 8

    if len(args) < 2:
        print('Not enough arguments')
        sys.exit(1)

    domain = args[0]
    if 'http://' not in domain and 'https://' not in domain:
        domain = 'http://' + domain

    if 'HERE' not in domain:
        print('"HERE" placeholder missing')
        sys.exit(1)

    wordlist = args[1]
    
    try:
        with open(wordlist, 'r') as file:
            words = file.read().split('\n')

    except Exception as e:
        print(f'Error: cannot read wordlist file "{wordlist}" because {e}')
    
    WORDS_COUNT = len(words)

    try:
        threadPool = Threadpool(threads)

        for word in words:
            threadPool.exec(check, (domain, word))
        
        while threadPool.queue:
            time.sleep(0.1)
        threadPool.killAll()
    
    except:
        print('\nAbort signal received, killing threads')
        threadPool.killAll()
