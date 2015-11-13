"""
Finds co-authors for the specified author from Google Scholar and dumps the JSON to a file.
"""

import bibtexparser
import grequests
import hashlib
import htmlentitydefs as htmlent
import optparse
import random
import re
import requests
import sys
import time
import os
import json

from bs4 import BeautifulSoup



def add_coauthor_info(author):

    coauthors_dict = {}

    html = open("../data/misc/"+author+"-source.html", "r").read()

    soup = BeautifulSoup(html, 'html.parser')

    try:
        table_rows = soup.find("tbody").findAll("tr", class_="gsc_a_tr")
        for row in table_rows:
            coauthors_dict[row.findAll("td")[0].find("a").text] = row.findAll("td")[0].find("div", class_="gs_gray").text.encode('utf-8')
            

    except Exception, e:
        raise e

    with open("../data/"+author+"/"+author+"-coauthors.json", "w") as outfile:
        json.dump(coauthors_dict, outfile)
    return






def main():
    parser = optparse.OptionParser(
        'Usage: python find_coauthors.py "AUTHOR"')
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("Please specify author name.")
        sys.exit(1)
    author = args[0].decode('utf-8')

    add_coauthor_info(author)
 	    

if __name__ == '__main__':
    main()
