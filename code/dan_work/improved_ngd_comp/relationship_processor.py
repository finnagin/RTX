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

"""
	Name: RelationshipProcessor
	Desc:
		This class contains methods
		that pre-processes
		relationships, and cache
		them into Redis.
"""
class RelationshipProcessor:
	def __init__(self):
		# setup redis connection
		self.r_instance = Redis()
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
		dict_to_from, dict_from_to = self.gen_dict(list_of_syns)
		to_from = 'to_from'
		from_to = 'from_to'
		# add both dicts into redis
		self.r_instance.hmset(to_from, dict_to_from)
		self.r_instance.hmset(from_to,  dict_from_to)

	def gen_dict(self, list_of_syns):
		to_from, from_to = list_of_syns
		to_from_dict = from_to_dict = defaultdict()

		for start, end in to_from:
			to_from_dict[start] = end
		from start, end in from_to_dict:
			from_to_dict[start] = end
		return (to_from_dict, from_to_dict)

	def targ_syn_decomp(self, query_list):
		starting_syn, target_syn = query_list
		decomp_target_syn = target_syn.split("|")
		if not decomp_target_syn:
			return query_list

		to_from_list = []
		to_from_list.append(list(product(syn_start, targets)))
		to_from_list.append(list(product(targets,syn_start)))
		return to_from_list