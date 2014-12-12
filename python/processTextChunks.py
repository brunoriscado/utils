#!/usr/bin/python
import concurrent
from concurrent.futures import as_completed
import re, sys

def process(event):
    entries = []
    fl = event[0]
    chunk = event[1]
    pat = event[2]
    f = open(fl, "rb")
    f.seek(chunk[0])
    for entry in pat.findall(f.read(chunk[1])):
       entries.append(entry)
    return entries

def getchunks(file, pat, size=1024*1024):
    f = open(file, "rb")
    while True:
        start = f.tell()
        f.seek(size, 1)
        s = f.readline() # skip forward to next line ending
        yield (file, (start, f.tell() - start), pat)
        if not s:
            break

if __name__ == "__main__":
    args = sys.argv
    if(args.size == 2):
        testFile = args[1]
        pat = re.compile(r".*?\n")
        results = []
    else:
        print ("specify the file")

    with concurrent.futures.ProcessPoolExecutor() as executor:
        for res in (executor.submit(process, event) for event in getchunks(testFile, pat)):
            results.append(res)

    for complete in as_completed(results):
        for entry in complete.result():
            print('Event result: %s' % entry)
