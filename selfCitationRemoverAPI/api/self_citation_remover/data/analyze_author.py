import json
from os import listdir
from os.path import isfile, join
import pprint
import matplotlib.pyplot as plt


author_list = ["Vahed Qazvinian"]

file_black_list = set(['.DS_Store','index.json','selfCitationInfo.json','index.txt'])


def get_author_list(paper_file):
	try:
		with open(paper_file,"r") as f:
			paper = json.loads(f.read())
			comma_separated_list = paper["author"].split(",")
			and_separatd_list = reduce(lambda x,y: x + y , [x.split("and") for x in comma_separated_list])
			return map(lambda x: x.strip().lower(), and_separatd_list)
	except Exception as e:
		print paper_file
		return []

def compute_own_citation(author_name,paper):
	count = 0
	for citing_paper in paper:
		author_list = paper[citing_paper]
		author_name_part_list = author_name.lower().split(" ")
		for author_name_part in author_name_part_list:
			if author_name_part in author_list:
				count += 1
	return count

def compute_collaborative_citation(paper):

	return 0

def compute_self_citation(paper):

	return 0

def plot_graphs(citation_detail):
	data = [(citation_detail[x]["own_citation"],citation_detail[x]["total_citation"]) for x in citation_detail]
	X = map(lambda x:x[0],data)
	Y = map(lambda y:y[1],data)

	plt.plot(X,Y,'g^')
	plt.show()

	return

def analyze_author(author_name):
	paper_folder_list = filter(lambda x:x not in file_black_list,listdir(author_name))
	paper_dict = {}
	for paper in paper_folder_list:
		paper_dict[paper] = {}
		citing_list = filter(lambda x:x not in file_black_list,listdir(author_name + "/" + paper))
		for citing_paper in citing_list:
			paper_dict[paper][citing_paper] = get_author_list(author_name + "/" + paper + "/" + citing_paper)
	# pprint.pprint(paper_dict)
	citation_detail = {}
	for paper in paper_dict:
		citation_detail[paper] = {}
		citation_detail[paper]["total_citation"] = len(paper_dict[paper])
		citation_detail[paper]["self_citation"] = compute_self_citation(paper_dict[paper])
		citation_detail[paper]["own_citation"] = compute_own_citation(author_name,paper_dict[paper])
		citation_detail[paper]["collaborative_citation"] = compute_collaborative_citation(paper_dict[paper])

	# print citation_detail
	plot_graphs(citation_detail)
	return

analyze_author(author_list[0])