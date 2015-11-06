"""
Finds self-citation papers for the specified author from Google Scholar.
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

#os.environ['NO_PROXY'] = 'scholar.google.com'

GSCHOLAR_BASE_URL = "https://scholar.google.com"
GSCHOLAR_QUERY_PATH = "/scholar"
MAX_PARALLEL_CONNECTIONS = 2
NO_OF_QUERIES = 0

##USER_AGENT = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36"
# Max permissible search results per page.
NR = 100


def _unescape_html_entities(html):
    # Author: Fredrik Lundh
    # http://effbot.org/zone/re-sub.htm#unescape-html
    def fixup(m):
        html = m.group(0)
        if html[:2] == "&#":
            # character reference
            try:
                if html[:3] == "&#x":
                    return chr(int(html[3:-1], 16))
                else:
                    return chr(int(html[2:-1]))
            except ValueError:
                pass
        else:
            # named entity9
            try:
                html = chr(htmlent.name2codepoint[html[1:-1]])
            except KeyError:
                pass
        return html

    return re.sub("&#?\w+;", fixup, html)


def _gen_fake_google_id():
    return hashlib.md5(str(random.random()).encode("utf-8")).hexdigest()[:16]


def _do_gscholar_request(path, gid, params={}):
    global NO_OF_QUERIES
    print 'params: ', params
    NO_OF_QUERIES += 1
    print "Queries done", NO_OF_QUERIES
    return requests.get(GSCHOLAR_BASE_URL + path,
                        params=params,
                        headers={
                            # Set CF = 4 in cookie to display BibTex citation link.
							##'user-agent' : USER_AGENT,
                            'cookie': 'GSP=ID=%s:CF=4:NR=%d' % (gid, NR)
                        })


def _is_actual_paper(title):
    return "CITATION" not in title


def _filter_title(title):
    return re.sub(r'\[.*\]', '', title).strip()


def _extract_bib_links(html):
    return [_unescape_html_entities(m) for m in \
     re.compile(r'<a href="(/scholar\.bib\?[^"]*)').findall(html)]


def _extract_bib_from_link(link, gid):
    return _do_gscholar_request(link, gid).text


def _is_self_citation(author, paper_authors):
    fname = author.split()[0].lower()
    lname = author.split()[-1].lower()
    for a in paper_authors.split("and"):
        if fname in a.lower() and lname in a.lower():
            return True
    return False


"""
Returns a list of tuples consisting of paper title and the 
corresponding citations url, for the specified author.
"""

def get_papers_by_author(author):
    query = 'author:"%s"' % author
    gid = _gen_fake_google_id()
    author_papers = []
    start = 0
    # Handles pagination. Currently just fetches the first page to reduce
    # network requests and avoid throttling.
    while start < NR:
        print 'start: ', start
        html = _do_gscholar_request(
            GSCHOLAR_QUERY_PATH, gid, {'q': query,
                                       'start': start}).text
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
        start += 20
        time.sleep(5)
    return author_papers


"""
Returns BibTex entries corresponding to the self-citation papers.
"""

def find_self_citations(author, paper):
    print 'finding self citations for: ', author, paper
    title, citations_url = paper
    gid = _gen_fake_google_id()
    start = 0
    total_citations = 0
    self_citation_info = {}
    self_citation_papers = []
    linkDict = {}
    linkID = 0

    while True:

    	## Commenting out the parallelization and increasing the sleep time

        # html = _do_gscholar_request(citations_url, gid, {'start': start}).text
        # links = [GSCHOLAR_BASE_URL + link for link in _extract_bib_links(html)]
        # print 'links: ', links
        # if len(links) == 0:
        #     break
        # total_citations += len(links)
        

        # # Create a set of unsent requests.
        # rs = (grequests.get(link,
        #                     headers={'Cookie': 'GSP=ID=%s:CF=4' % gid})
        #       for link in links)
        # # Send requests in parallel. Throttle to MAX_PARALLEL_CONNECTIONS.
        # resp = grequests.map(rs, size=MAX_PARALLEL_CONNECTIONS)
        # for r in resp:
        #     bib = bibtexparser.loads(r.text).entries[0]
        #     print bib
        #     if _is_self_citation(author, bib['author']):
        #         print '    #### found self-citation...'
        #         self_citation_papers.append(bib)
        # start += NR
        # time.sleep(2)

        # for link in links:
        #     bib = bibtexparser.loads(link.text).entries[0]
        #     print bib
        #     if _is_self_citation(author, bib['author']):
        #         print '    #### found self-citation...'
        #         self_citation_papers.append(bib)
        #     time.sleep(random.randint(30,40))

        # start += NR

        html = _do_gscholar_request(citations_url, gid, {'start': start}).text
        links = _extract_bib_links(html)
        if len(links) == 0:
            break
        total_citations += len(links)

        

        for link in links:
        	linkDict[link] = linkID
        	linkID += 1

        

        for link in links:

            linkFileName = "../data/"+author + "/"+ paper[0]  + "/paper"+ str(linkDict[link]) + ".json"
            bib = {}
            
            if not os.path.exists(linkFileName):

                bib = bibtexparser.loads(_extract_bib_from_link(
                    link, gid)).entries[0]
                print bib
                slpTime = random.randint(15, 20)
                print "Sleeping ", slpTime, " seconds..."
                time.sleep(slpTime)

                with open(linkFileName, "w") as outfile:
                    json.dump(bib, outfile)

            else:

                with open(linkFileName, "r") as data_file:
                    bib = json.load(data_file)

                print bib

            
            if _is_self_citation(author, bib['author']):
                print '    #### found self-citation...'
                self_citation_papers.append(bib)
                
        slpTime = random.randint(10, 15)
        print "Sleeping ", slpTime, " seconds..."
        time.sleep(slpTime)

        start += NR


    with open("../data/" + author + "/" + paper[0] + "/index.json", "w") as linkIndex:
        json.dump(linkDict, linkIndex)
        print "Dumped data to " + "../data/" + author + "/" + paper[0] + "/index.json"

    try:
        self_citation_info['ratio'] = float(
            len(self_citation_papers)) / total_citations
    except Exception as e:
        self_citation_info['ratio'] = -1.0;
    self_citation_info["total_citations"] = total_citations
    self_citation_info["self_citation_papers"] = len(self_citation_papers)
    self_citation_info['papers'] = self_citation_papers

    print self_citation_info
    print '-------------------------------------------------------------------'
    print 'percentage of self-citations for this paper: %f' % \
        (100.0 * self_citation_info['ratio'])

    return self_citation_info


def main():
    parser = optparse.OptionParser(
        'Usage: python self-citation-remover.py "AUTHOR"')
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("Please specify author name.")
        sys.exit(1)
    author = args[0]
    papers = get_papers_by_author(author)
    print 'papers by %s:' % author
    print papers
    if len(papers) == 0:
        print 'blocked! exiting ...'
        sys.exit()

    ## Check if folder for an author exists and create one if it doesn't

    if not os.path.exists("../data/" + author):
    	os.makedirs("../data/" + author)


    for paper in papers:
        

        
        paperFolderPath = "../data/" + author + "/" + paper[0]

        ## Check if info for paper already exists (in a JSON) and make the call if it doesn't

        if not os.path.exists(paperFolderPath):
        	os.makedirs(paperFolderPath)


        if os.path.exists(paperFolderPath + "/index.json"):
        	## If index exists, the paper is already completed
        	continue

    	startTime = time.time()
    	self_citation_info = find_self_citations(author, paper)
    	endTime = time.time()
    	print "The last paper took ", str(endTime-startTime), " seconds to compute self citations."

        
    	with open(paperFolderPath + "/selfCitationInfo.json", 'w') as outfile:
    		json.dump(self_citation_info, outfile)
			
		print "Written self citation info for " + paper[0] + " to file location : " + paperFolderPath


		print '-------------------------------------------------------------------'
		print 'self-citation details for this paper:'
		print self_citation_info	    

if __name__ == '__main__':
    main()
