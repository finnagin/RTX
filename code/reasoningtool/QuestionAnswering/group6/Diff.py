# Point of this script is to ingest two 0.9.0 spec outputs and perform comparisons between them
import json
import networkx as nx
#res1_json = json.load(open('gamma_ebola_p9.json', 'r'))
#res1_json = json.load(open('fake_ebola_p9.json', 'r'))

class Diff():
	def __init__(self):
		self.input1 = None
		self.input2 = None

	def populate(self, fid1, fid2):
		"""
		Populate the class with the json info
		:param fid1: file stream for first json object
		:param fid2: file stream for the other json object
		:return: None
		"""
		self.input1 = json.load(fid1)
		self.input2 = json.load(fid2)

	def same_query_plan_types(self):
		"""
		Check if both the inputs are using the same query plan where "same" is defined to be as going through the same
		node types, with the same edge directions. I.e. are the query plans isomorphic, where nodes are considered
		identical if they have the same type. Note: this will say some plans are the same when they really aren't
		:return: Boolean
		"""
		if self.input1 is None or self.input2 is None:
			raise Exception("Missing input: please run the populate() method first")
		g1 = nx.DiGraph()
		g2 = nx.DiGraph()

		# populate the nodes
		for node in self.input1['question_graph']['nodes']:
			g1.add_node(node['id'], {"type": node['type']})

		for node in self.input2['question_graph']['nodes']:
			g2.add_node(node['id'], {"type": node['type']})

		# populate the edges
		for edge in self.input1['question_graph']['edges']:
			g1.add_edge(edge['source_id'], edge['target_id'])

		for edge in self.input2['question_graph']['edges']:
			g2.add_edge(edge['source_id'], edge['target_id'])

		return nx.is_isomorphic(g1, g2, node_match=lambda x, y: x['type'] == y['type'])

	def same_node_types(self, node1, node2):
		"""
		Checks if two nodes (one from each response) are of the same type according to their respective query plans
		:param node1: a node_binding key
		:param node2: a node_binding key
		:return: Boolean
		"""
		if self.input1 is None or self.input2 is None:
			raise Exception("Missing input: please run the populate() method first")
		# TODO finsih it
		return self.input1['question_graph']['nodes'][node1] == self.input2['question_graph']['nodes'][node2]




################################################
# Brief error checking
def same_query_plan_types():
	d = Diff()
	d.populate(open('gamma_ebola_p9.json', 'r'), open('fake_ebola_p9.json', 'r'))
	assert d.same_query_plan_types()


def run_tests():
	same_query_plan_types()



#######################################################3
# Testing
d = Diff()
d.populate(open('gamma_ebola_p9.json', 'r'), open('fake_ebola_p9.json', 'r'))
d.same_node_types('n0', 'n0')
