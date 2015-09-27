import json

from django.shortcuts import render
from django.http import HttpResponse
from self_citation_remover import self_citation_remover

import requests
import urllib

def getAuthorInfo(request):
    authorName = request.GET.get('name', None)
    if authorName:
        # return HttpResponse(json.dumps({"response_json":json.dumps(
        #     self_citation_remover.get_papers_by_author(authorName)),"success":"true"}))
        return HttpResponse(json.dumps(self_citation_remover.get_papers_by_author(authorName)))
    else:
        return HttpResponse("Usage: Add query parameter 'name'")


def getSelfCitations(request):
    authorName = request.GET.get('name', None)
    paperTitle = request.GET.get('title', None)
    citationsURL = request.GET.get('url', None)
    print "Attempting to get : ", citationsURL
    if authorName and paperTitle and citationsURL:
        return HttpResponse(json.dumps(
            self_citation_remover.find_self_citations(authorName, (
                paperTitle, citationsURL))))
    else:
        return HttpResponse(
            "Usage: Add query parameters 'name', 'title' and 'url'")

def getAuthorInfo_local(request):
    name = request.GET.get('name', None)
    data = {}
    data["name"] = name
    url = "http://social-comp.elasticbeanstalk.com/getAuthorInfo"
    param_text = urllib.urlencode(data)
    r = requests.get(url + '?' + param_text)

    # print r.text

    return HttpResponse(r.text)

def getSelfCitations_local(request):
    name = request.GET.get('name', None)
    title = request.GET.get('title', None)
    url = request.GET.get('url', None)

    data = {}
    data["name"] = name
    data["title"] = title
    data["url"] = url
    url = "http://social-comp.elasticbeanstalk.com/getSelfCitations"
    param_text = urllib.urlencode(data)
    r = requests.get(url + '?' + param_text)

    return HttpResponse(r.text)
    