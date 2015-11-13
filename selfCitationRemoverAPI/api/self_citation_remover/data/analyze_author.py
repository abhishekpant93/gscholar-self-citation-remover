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
			# print citing_author_set
			# print collab_set
			# print '************************'
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


def plot_separate_graphs(citation_detail_dict):
	for author_name in citation_detail_dict:
		citation_detail = citation_detail_dict[author_name]
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

		fit_own = np.polyfit(X_own,Y_own,3)
		fit_fn_own = np.poly1d(fit_own)

		fit_collab = np.polyfit(X_collab,Y_collab,3)
		fit_fn_collab = np.poly1d(fit_collab)

		plt.plot(X_self,Y_self,'r^',label = 'self')
		plt.plot(X_own,Y_own,'g^',label = 'own')
		plt.plot(X_collab,Y_collab,'b^',label = 'collaborative')
		plt.plot(sorted(X_self),fit_fn_self(sorted(X_self)),'r')
		plt.plot(sorted(X_own),fit_fn_own(sorted(X_own)),'g')
		plt.plot(sorted(X_collab),fit_fn_collab(sorted(X_collab)),'b')
		plt.legend(loc='upper left')
		plt.ylim([0,max_Y])
		file_name = author_name.replace(' ','').replace('.','')
		plt.savefig(file_name + '_all.eps', format='eps', dpi=1000)
		plt.cla()


	return

def plot_together_graphs(citation_detail_dict):
	max_X = -1
	max_Y = -1
	style_list = ['^','o']
	line_style_list = ['','--']
	i = 0
	for author_name in citation_detail_dict:
		citation_detail = citation_detail_dict[author_name]
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


		max_X = max(max_X,max(X_own + X_self + X_collab))
		max_Y = max(max_Y,max(Y_own + Y_self + Y_collab))

		fit_self = np.polyfit(X_self,Y_self,3)
		fit_fn_self = np.poly1d(fit_self) 

		fit_own = np.polyfit(X_own,Y_own,3)
		fit_fn_own = np.poly1d(fit_own)

		fit_collab = np.polyfit(X_collab,Y_collab,3)
		fit_fn_collab = np.poly1d(fit_collab)

		style = style_list[i]
		line_style = line_style_list[i]

		plt.plot(X_self,Y_self,'r' + style,label = 'self-' + author_name)
		plt.plot(X_own,Y_own,'g' + style,label = 'own-' + author_name)
		plt.plot(X_collab,Y_collab,'b' + style,label = 'collaborative-' + author_name)
		plt.plot(sorted(X_self),fit_fn_self(sorted(X_self)),'r' + line_style)
		plt.plot(sorted(X_own),fit_fn_own(sorted(X_own)),'g' + line_style)
		plt.plot(sorted(X_collab),fit_fn_collab(sorted(X_collab)),'b' + line_style)
		plt.legend(loc='upper left',prop={'size':10	})
		i += 1
	plt.ylim([0,max_Y])
	plt.savefig('all.eps', format='eps', dpi=1000)
	return

def analyze_author(author_name_list):
	citation_detail = {}
	for author_name in author_name_list:
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
		citation_detail[author_name] = {}
		for paper in paper_dict:
			citation_detail[author_name][paper] = {}
			citation_detail[author_name][paper]["total_citation"] = len(paper_dict[paper])
			try:
				citation_detail[author_name][paper]["self_citation"] = compute_collaborative_citation(paper_dict[paper],side_author_dict[paper])
			except Exception as e:
				citation_detail[author_name][paper]["self_citation"] = -1
				# print str(e)
				# print 'in main loop = {' + paper + '}'
			citation_detail[author_name][paper]["own_citation"] = compute_own_citation(author_name,paper_dict[paper])
			citation_detail[author_name][paper]["collaborative_citation"] = compute_collaborative_citation(paper_dict[paper],collab_set)

		# print citation_detail
	plot_separate_graphs(citation_detail)
	plot_together_graphs(citation_detail)
	return

analyze_author(author_list)