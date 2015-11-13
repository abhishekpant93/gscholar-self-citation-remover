import json
from os import listdir
from os.path import isfile, join
import pprint
import matplotlib.pyplot as plt


author_list = ["Vahed Qazvinian"]

file_black_list = set(['.DS_Store','index.json','selfCitationInfo.json','index.txt','Vahed Qazvinian-coauthors.json'])

def normalize_paper_name(paper_name):
	paper_name = paper_name.replace('.','').replace('-','')
	paper_name = paper_name.lower().decode('utf-8').encode('ascii','ignore')
	return paper_name

def get_author_list(paper_file):
	try:
		with open(paper_file,"r") as f:
			paper = json.loads(f.read())
			comma_separated_list = paper["author"].split(",")
			and_separated_list = reduce(lambda x,y: x + y , [x.split("and") for x in comma_separated_list])
			space_separatd_list = reduce(lambda x,y: x + y , [x.split(" ") for x in and_separated_list])
			return map(lambda x: x.strip().lower(), space_separatd_list)
	except Exception as e:
		print str(e	)
		print paper_file
		return []



def get_collaboration_set(author_name):
	file_path = author_name + '/' + author_name + '-coauthors.json'
	# print file_path	
	with open(file_path,'rb') as f:
		collab_dict = json.loads(f.read())
		side_author_dict = {}
		collab_set = set([])
		for paper in collab_dict:
			comma_separated_list = collab_dict[paper].split(",")
			and_separated_list = reduce(lambda x,y: x + y , [x.split("and") for x in comma_separated_list])
			space_separated_list = map(lambda x:x.strip().lower(),reduce(lambda x,y: x + y , [x.split(" ") for x in and_separated_list]))
			side_author_dict[normalize_paper_name(paper)] = set(space_separated_list)
			collab_set = collab_set.union(side_author_dict[normalize_paper_name(paper)])
		return collab_set,side_author_dict



def compute_collaborative_citation(paper,collab_set):
	try:
		count = 0
		for citing_paper in paper:
			citing_author_set = set(paper[citing_paper])
			print citing_author_set
			print collab_set
			print '************************'
			if len(citing_author_set.intersection(collab_set)) > 0:
				count += 1
		return count
	except Exception as e:
		print 'in collab : ' + str(e)
		return -1


def compute_own_citation(author_name,paper):
	count = 0
	for citing_paper in paper:
		citing_author_set = set(paper[citing_paper])
		author_name_part_set = set(author_name.lower().split(" "))
		if len(citing_author_set.intersection(author_name_part_set)) > 0:
			count += 1
	return count

def plot_graphs(citation_detail):
	data = [(citation_detail[x]["collaborative_citation"],citation_detail[x]["total_citation"]) for x in citation_detail]
	good_data = filter(lambda x: x[0] >= 0 and x[1] >= 0,data)

	X = map(lambda x:x[0],good_data)
	Y = map(lambda y:y[1],good_data)



	plt.plot(X,Y,'g^')
	plt.show()

	return

def analyze_author(author_name):
	paper_folder_list = filter(lambda x:x not in file_black_list,listdir(author_name))
	paper_dict = {}
	for paper in paper_folder_list:
		paper_dict[normalize_paper_name(paper)] = {}
		citing_list = filter(lambda x:x not in file_black_list,listdir(author_name + "/" + paper))
		for citing_paper in citing_list:
			paper_dict[normalize_paper_name(paper)][normalize_paper_name(citing_paper)] = get_author_list(author_name + "/" + paper + "/" + citing_paper)
	# pprint.pprint(paper_dict)
	collab_set,side_author_dict = get_collaboration_set(author_name)

	# print collab_set

	# print side_author_dict
	# pprint.pprint(side_author_dict.keys())
	citation_detail = {}
	for paper in paper_dict:
		citation_detail[paper] = {}
		citation_detail[paper]["total_citation"] = len(paper_dict[paper])
		try:
			citation_detail[paper]["self_citation"] = compute_collaborative_citation(paper_dict[paper],side_author_dict[paper])
		except Exception as e:
			citation_detail[paper]["self_citation"] = -1
			# print str(e)
			print 'in main loop = {' + paper + '}'
		citation_detail[paper]["own_citation"] = compute_own_citation(author_name,paper_dict[paper])
		citation_detail[paper]["collaborative_citation"] = compute_collaborative_citation(paper_dict[paper],collab_set)

	# print citation_detail
	plot_graphs(citation_detail)
	# print get_collaboration_set(author_name)
	return

analyze_author(author_list[0])