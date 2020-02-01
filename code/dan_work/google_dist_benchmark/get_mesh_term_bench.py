import cypher
import sys
import shutil
import networkx as nx
import os
sys.path.append('./old_code_for_benchmark_purpose')
sys.path.append('../../reasoningtool/kg-construction')
sys.path.append('../../reasoningtool/QuestionAnswering')

from NormGoogleDistance import NormGoogleDistance

from ReasoningUtilities import return_subgraph_through_node_labels
from ReasoningUtilities import get_graph
from ReasoningUtilities import connection
from ReasoningUtilities import defaults
from bench_mark_decorator import bench_harness

"""
	Name: BenchUtils
	Author: Daniel Lin
	Description:
		This class contains utility
		functions needed to perform
		benchmarking for the normalized
		google distance.
"""
class BenchUtils:
	"""
		name: generate_graph
		input:
			count: number of nodes to limit
		output:
			G: graph from neo4j
		description:
			queries a graph from neo4j.
	"""
	def generate_graph(self, count):
		neo4j_query = "match \
					  path=(s)-[]-(:protein)-[]-(t:anatomical_entity {id: 'UBERON:0001474'}) \
					  return path limit %d;" %(count)
		res = cypher.run(neo4j_query, conn=connection, config=defaults)
		directed = True
		return get_graph(res, directed=directed)
	"""
		name: get_list_edges_data
		input:
			node_attrs: node attributes from neo4j
			node_edges: node and edge data
		output:
			res:
		description:
			return a list of curie id
			and ndoe dscription from
			the neo4j graph.
	"""
	def get_list_edges_data(self, node_attrs, node_edges):
		nodes, edges = node_edges
		descriptions, curie_id, labels = node_attrs
		context_node_id = context_node_descr = None
		res = []
		for (edge_one, edge_two) in edges:
			source_id, target_id = curie_id[edge_one], curie_id[edge_two]
			source_descr, target_descr = descriptions[edge_one], descriptions[edge_two]
			if context_node_id and context_node_descr:
				desc = [source_descr, target_descr, context_node_descr]
				curi_id = [source_id, target_id, context_node_id]
				res.append([curi_id, desc])
			else:
				curi_id = [source_id, target_id]
				desc = [source_descr, target_descr]
				res.append([curi_id, desc])
		return res
	"""
		name: gen_node_attributes
		input:
			g: graph from neo4j
		output:
			descriptions: node description
			curie_id: node' curie id
			labels: node labels
		description:
			gets the node's description, curie_id,
			and labels.
	"""
	def gen_node_attributes(self, g):
		descriptions = nx.get_node_attributes(g, 'description')
		curie_id = nx.get_node_attributes(g, 'id')
		labels = nx.get_node_attributes(g, 'labels')
		return (descriptions, curie_id, labels)
	"""
		name: gen_node_attributes
		input:
			g: graph from neo4j
		output:
			descriptions: node description
			curie_id: node' curie id
			labels: node labels
		description:
			gets the node's description, curie_id,
			and labels.
	"""
	def gen_node_edges(self, g):
		nodes = list(nx.nodes(g))
		edges = list(nx.edges(g))
		return (nodes, edges)
"""
	Name: Bench_GetMeshForAll
	Description:
		Class to benchmark
		get_mesh_term_for_all
"""
class Bench_GetMeshForAll:
	def __init__(self):
		self.google_dist = NormGoogleDistance()
		self.bench_utils = BenchUtils()
		g = self.bench_utils.generate_graph()
		node_attrs = self.bench_utils.gen_node_attributes(g)
		node_edges = self.bench_utils.gen_node_edges(g)
		self.test_data = self.bench_utils.get_list_edges_data(node_attrs, node_edges)
	"""
		name: bench_get_mesh_for_all
		input: None
		output: None
		description:
			generates the timing for get_mesh_term_for_all.
	"""
	@bench_harness(file_name='get_mesh_for_all', fun_name='bench_get_mesh_for_all')
	def bench_get_mesh_for_all(self):
		for curie_ids, descs in self.test_data:
			terms = [None] * len(curie_ids)
			for a in range(len(descs)):
				terms[a] = self.google_dist.get_mesh_term_for_all(curie_ids[a], descs[a])

if __name__ == '__main__':
	# clean out cached result for better
	# testing result.
	if os.path.isfile('./orangeboard.sqlite'):
		os.remove('./orangeboard.sqlite')
	if os.path.isdir('./.web_cache'):
		shutil.rmtree('./.web_cache')
	bench_mark = Bench_GetMeshForAll()
	bench_mark.bench_get_mesh_for_all()