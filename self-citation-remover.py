"""
Removes self-citations for the specified author from Google Scholar.
"""

import hashlib
import optparse
import random
import re
import requests
import time

from bs4 import BeautifulSoup

GSCHOLAR_BASE_URL = "http://scholar.google.com"
GSCHOLAR_QUERY_PATH = "/scholar"
# Max permissible search results per page.
NR = 20

def _gen_fake_google_id():
	return hashlib.md5(str(random.random()).encode("utf-8")).hexdigest()[:16]

def _do_gscholar_request(path, gid, params={}):
	print 'params: ', params
  	return requests.get(GSCHOLAR_BASE_URL + path, params=params,
  	headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) \
  	AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9',
  	# Set CF = 4 in cookie to display BibTex citation link.
       'Cookie': 'GSP=ID=%s:CF=4:NR=%d' % (gid, NR)})

def _is_actual_paper(title):
	return "CITATION" not in title

def _filter_title(title):
	return re.sub(r'\[.*\]', '', title).strip()

"""
Returns a list of tuples consisting of paper title and the 
corresponding citations url, for the specified author.
"""
def get_papers_by_author(author):
	query = 'author:"%s"' % author
	gid = _gen_fake_google_id()
	author_papers = []
	# Handle pagination.
	start = 0
	while True:
		print 'start: ', start
		html = _do_gscholar_request(
			GSCHOLAR_QUERY_PATH, gid, {'q':query, 'start': start}).text
		soup = BeautifulSoup(html, 'html.parser')
		papers = soup.findAll("div", class_="gs_ri")
		if len(papers) == 0:
			break
		for p in papers:
			try:
				title = p.find("h3", class_="gs_rt").text
				if not _is_actual_paper(title):
					continue
				cites = p.find("div", class_="gs_fl").find("a")
				if "Cited by" in cites.text:
					author_papers.append((_filter_title(title), cites['href']))
			except Exception, e:
				raise e
		start += NR
		time.sleep(5)
	return author_papers

def main():
	parser = optparse.OptionParser(
		'Usage: python self-citation-remover.py "AUTHOR"')
	(options, args) = parser.parse_args()
	if len(args) != 1:
		parser.error("Please specify author name.")
		sys.exit(1)
	author = args[0]
	print get_papers_by_author(author)

if __name__ == '__main__':
	main()