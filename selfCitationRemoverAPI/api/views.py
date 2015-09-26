import json

from django.shortcuts import render
from django.http import HttpResponse
from self_citation_remover import self_citation_remover

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