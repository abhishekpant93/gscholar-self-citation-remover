import json
from os import listdir
from os.path import isfile, join
import pprint
import numpy as np
import matplotlib.pyplot as plt


author_list = ["Vahed Qazvinian","Ginevra Castellano"]

file_black_list = set(['.DS_Store','index.json','selfCitationInfo.json','index.txt','Vahed Qazvinian-coauthors.json','Ginevra Castellano-coauthors.json'])

def normalize_paper_name(paper_name):
	paper_name = paper_name.replace('.','').replace('-','')
	paper_name = paper_name.lower()
	try:
		paper_name = paper_name.decode('utf-8')
	except Exception as e:
		paper_name = paper_name.encode('ascii','ignore')
	return paper_name

def get_author_list(paper_file):
	try:
		with open(paper_file,"r") as f:
			paper = json.loads(f.read())
			comma_separated_list = paper["author"].split(",")
			and_separated_list = reduce(lambda x,y: x + y , [x.split("and") for x in comma_separated_list])
			space_separatd_list = filter(lambda x:x!='',reduce(lambda x,y: x + y , [x.split(" ") for x in and_separated_list]))
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
			space_separated_list = filter(lambda x:x!='',map(lambda x:x.strip().lower(),reduce(lambda x,y: x + y , [x.split(" ") for x in and_separated_list])))
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
	own_citation = [(citation_detail[x]["total_citation"],citation_detail[x]["own_citation"]) for x in citation_detail]
	self_citation = [(citation_detail[x]["total_citation"],citation_detail[x]["self_citation"]) for x in citation_detail]
	collab_citation = [(citation_detail[x]["total_citation"],citation_detail[x]["collaborative_citation"]) for x in citation_detail]
	

	own_citation = filter(lambda x: x[0] >= 0 and x[1] >= 0,own_citation)
	self_citation = filter(lambda x: x[0] >= 0 and x[1] >= 0,self_citation)
	collab_citation = filter(lambda x: x[0] >= 0 and x[1] >= 0,collab_citation)

	X_own = map(lambda x:x[0],own_citation)
	Y_own = map(lambda y:y[1],own_citation)

	X_self = map(lambda x:x[0],self_citation)
	Y_self = map(lambda y:y[1],self_citation)

	X_collab = map(lambda x:x[0],collab_citation)
	Y_collab = map(lambda y:y[1],collab_citation)


	max_X = max(X_own + X_self + X_collab)
	max_Y = max(Y_own + Y_self + Y_collab)

	fit_self = np.polyfit(X_self,Y_self,3)
	fit_fn_self = np.poly1d(fit_self) 
	# plt.plot(X_self,Y_self,'r^',sorted(X_self),fit_fn_self(sorted(X_self)),'r')
	# plt.ylim([0,max_Y])
	# # plt.show()
	# plt.savefig('self.eps', format='eps', dpi=1000)



	fit_own = np.polyfit(X_own,Y_own,3)
	fit_fn_own = np.poly1d(fit_own)
	plt.plot(X_own,Y_own,'g^',sorted(X_own),fit_fn_own(sorted(X_own)),'g')
	plt.ylim([0,max_Y])
	# plt.show()
	plt.savefig('own.eps', format='eps', dpi=1000)


	fit_collab = np.polyfit(X_collab,Y_collab,3)
	fit_fn_collab = np.poly1d(fit_collab)
	plt.plot(X_collab,Y_collab,'b^',sorted(X_collab),fit_fn_collab(sorted(X_collab)),'b')
	plt.ylim([0,max_Y])
	# plt.show()
	plt.savefig('collab.eps', format='eps', dpi=1000)

	plt.plot(X_self,Y_self,'r^',label = 'self')
	plt.plot(X_own,Y_own,'g^',label = 'own')
	plt.plot(X_collab,Y_collab,'b^',label = 'collaborative')
	plt.plot(sorted(X_self),fit_fn_self(sorted(X_self)),'r')
	plt.plot(sorted(X_own),fit_fn_own(sorted(X_own)),'g')
	plt.plot(sorted(X_collab),fit_fn_collab(sorted(X_collab)),'b')
	plt.legend(loc='upper left')
	plt.ylim([0,max_Y])
	plt.savefig('all.eps', format='eps', dpi=1000)


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

analyze_author(author_list[1])