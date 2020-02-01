import cypher
import sys
sys.path.append('../reasoningtool/QuestionAnswering')

from networkx import weakly_connected_components
from ReasoningUtilities import get_graph
from ReasoningUtilities import connection
from ReasoningUtilities import defaults
from ReasoningUtilities import test_weight_graph_with_google_distance

class GraphOperations:
	# weakly connected components analysis class
	# run thins in the background with nohup
	def __init__(self):
		self.network_interface = Neo4jInterface()
	def get_weak_component(self, G):
		return weakly_connected_components(G)
	def equiv_all_graph(self):
		print("Getting equivalent_to for entire graph")
		g = self.network_interface._get_equivalent_to_graph()
		return self.get_weak_component(g)
	def close_match_all_graph(self):
		print("Getting close_match for entire graph")
		g = self.network_interface._get_close_match_graph()
		return self.get_weak_component(g)
	def get_equivalent_to_compact(self):
		print("Getting equivalent_to for partial graph")
		g = self.network_interface._get_equivalent_to_compact()
		return self.get_weak_component(g)
	def get_close_match_compact(self):
		print("Getting close_match for partial graph")
		g = self.network_interface._get_close_match_compact()
		return self.get_weak_component(g)

class Neo4jInterface:
	# get graph from our neo4j database kg2endpoint2.rtx.ai
	def _get_equivalent_to_graph(self):
		query = 'MATCH p=(n)-[r:equivalent_to]->(m) RETURN p'
		return get_graph(cypher.run(query, conn=connection, config=defaults), directed=False)
	def _get_close_match_graph(self):
		query = 'MATCH p=(n)-[r:close_match]->(m) RETURN p'
		return get_graph(cypher.run(query, conn=connection, config=defaults), directed=False)
	def _get_equivalent_to_compact(self):
		query = 'MATCH (n)-[r:equivalent_to]->(m) RETURN n.id, type(r), r.provided_by'
		return get_graph(cypher.run(query, conn=connection, config=defaults), directed=False)
	def _get_close_match_compact(self):
		query = 'MATCH (n)-[r:close_match]->(m) RETURN n.id, type(r), r.provided_by'
		return get_graph(cypher.run(query, conn=connection, config=defaults), directed=False)

if __name__ == '__main__':
	g_ops = GraphOperations()
	g_ops.equiv_all_graph()
	g_ops.close_match_all_graph()
	g_ops.get_equivalent_to_compact()
	g_ops.get_close_match_compact()
