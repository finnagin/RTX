import sys
sys.path.append(".")
sys.path.append("..")

from RelationshipProcessor import RedisRelationshipCaching

from unittest import TestCase
from unittest import main
from ast import literal_eval

class RelationshipProcessorTests(TestCase):
	def setUp(self):
		self.relation_process = RedisRelationshipCaching()
	def test_caching_simple_predicate(self):
		# sample data taken from weighted_norm_dist google
		simple_test_case = [['intercellular adhesion molecule 1', 'malaria']]
		mock_score = [[173, 17444, 64501]]
		to_from_dict = self.relation_process.gen_dict(simple_test_case, mock_score)
		self.relation_process.cache_syn_to_redis(to_from_dict)
		r_inst = self.relation_process.get_redis_instance()
		test_data = simple_test_case[0][0]
		res = literal_eval(r_inst.get(test_data).decode('utf-8'))
		test_res = literal_eval(res[0])
		self.assertEqual("malaria", test_res[0])

	def test_caching_compound_predicate(self):
		simple_test_case = [['intercellular adhesion molecule 1', 'malaria|protein|XY|YZ']]
		query_list = self.relation_process.start_target_syn_decomp(simple_test_case[0])
		expected_res = [[('intercellular adhesion molecule 1', 'malaria'), \
						 ('intercellular adhesion molecule 1', 'protein'), \
						 ('intercellular adhesion molecule 1', 'XY'), \
						 ('intercellular adhesion molecule 1', 'YZ'), \
						 ('malaria', 'protein'), ('malaria', 'XY'), \
						 ('malaria', 'YZ'), ('protein', 'XY'), \
						 ('protein', 'YZ'), ('XY', 'YZ')], \
						 ('intercellular adhesion molecule 1','malaria|protein|XY|YZ')]
		self.assertEqual(expected_res, query_list)

if __name__ == '__main__':
	main()