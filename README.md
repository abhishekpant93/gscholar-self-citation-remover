# Google Scholar Self-Citation Remover
An app to compute citation metrics for an author from Google Scholar after removing self-citations.

## Usage
The standalone self\_citation\_remover script is located [here] (https://github.com/abhishekpant93/gscholar-self-citation-remover/tree/master/selfCitationRemoverAPI/api/self_citation_remover).

Currently, this fetches a list of papers by the author, and finds the self-citations for the first paper in the list.
```
python self_citation_remover.py "author"
```