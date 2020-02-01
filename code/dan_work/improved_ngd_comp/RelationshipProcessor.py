__author__ = 'Daniel Lin '
__copyright__ = 'Oregon State University'
__credits__ = ['Daniel Lin']
__license__ = 'MIT'
__version__ = '0.1.0'
__maintainer__ = 'Daniel Lin'
__email__ = 'danieltzulin@gmail.com'
__status__ = 'Prototype'

from itertools import product
from collections import defaultdict
from redis import Redis
from config_file import host_name
from config_file import port_name
import json
from ast import literal_eval
from itertools import combinations
"""
	Name: RedisRelationshipCaching
	Desc:
		This class contains methods
		that pre-processes
		relationships, and cache
		them into Redis.
"""
class RedisRelationshipCaching:
	def __init__(self):
		# setup redis connection
		self.r_instance = Redis(host=host_name, port=port_name)
	def cache_syn_to_redis(self, list_of_syns):
		"""
			put a list of synonyms into redis.
			The redis cache's form, for
			both to_from and from_to set, should be:
			{
				key: starting_syn, val:[
											(target_syn_1, score_1),
											(target_syn_2, score_2),...
											(target_syn_N, score_N),...
									   ]
			}
			where score = [
							count_starting_syn AND target_syn_N,
							count_starting_syn,
							count_target_syn_N
						  ]
		"""
		to_from, from_to = list_of_syns
		for i, val in enumerate(to_from):
			start, end = val[0], str((val[1], val[2]))
			if self.r_instance.exists(start):
				val = literal_eval(self.r_instance.get(start).decode('utf-8'))
				val.append(end)
				self.r_instance.set(start, str(val))
			else:
				self.r_instance.set(start, str([end]))

		for j, val in enumerate(from_to):
			score_reversed = [val[2][0], val[2][2], val[2][1]]
			start, end = val[0], str((val[1], score_reversed))
			if self.r_instance.exists(start):
				val = literal_eval(self.r_instance.get(start).decode('utf-8'))
				val.append(end)
				self.r_instance.set(start, str(val))
			else:
				self.r_instance.set(start, str([end]))
	def gen_dict(self, list_of_syns, score_arrs):
		to_from, from_to = [],[]
		for i, (start, end) in enumerate(list_of_syns):
			# redis doesn't like tuples, so change the
			# tuple into a string
			to_from.append((start,end, score_arrs[i]))
		for j, (start, end) in enumerate(list_of_syns):
			from_to.append((end, start, score_arrs[j]))
		return (to_from, from_to)

	def start_target_syn_decomp(self, query_list):
		starting_syn, target_syn = query_list
		decomp_target_syns = target_syn.split("|")
		if not decomp_target_syns:
			return query_list
		total_list = [starting_syn]
		for decomp_target_syn in decomp_target_syns:
			total_list.append(decomp_target_syn)
		to_from_list = []
		to_from_list.append(list(combinations(total_list, 2)))
		to_from_list.append((starting_syn, query_list[1]))
		return to_from_list

	def get_redis_instance(self):
		return self.r_instance
