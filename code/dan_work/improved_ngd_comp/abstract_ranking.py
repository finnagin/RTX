__author__ = 'Daniel Lin '
__copyright__ = 'Oregon State University'
__credits__ = ['Daniel Lin']
__license__ = 'MIT'
__version__ = '0.1.0'
__maintainer__ = 'Daniel Lin'
__email__ = 'danieltzulin@gmail.com'
__status__ = 'Prototype'
from collections import defaultdict
"""
	Name: AbstractRanking
	Desc:
		This class contains
		all of the methods
		for processing our
		abstract text.
"""
from redis import Redis
from collections import Counter

class AbstractRanking:
	def __init__(self):
		self.r_inst = Redis()
	def put_abstract_into_redis(self, keys_dicts_for_abs, abs_corp):
		for i, (key, dict_word_cnt) in keys_dicts_for_abs:
			self.r_inst.hmset(key, dict_word_cnt)
			second_set_key = "".join([str(key), str(i)])
			self.r_inst.sadd(second_set_key, abs_corp[key])

	def AND_term_search(self, key1, key2):
		"""
			intersect corresponding abstract
			on redis
		"""
		intersects =  self.r_inst.sinter(key1, key2)
		if not intersects:
			return (False, [])
		return (True, intersects)
	def OR_term_search(self, keys, target):
		res = []
		for key in keys:
			word_dict = self.r_inst.get(key)
			if target in word_dict:
				res.append(key)
			else:
				res.append("NONE")
		if all(res == "NONE"):
			return (False, [])
		return (True, res)
	def count_word_in_corpus(self, abs_corpus):
		return Counter(abs_corpus)
	def gen_corp_dict(self, abstracts):
		keys_dicts_for_abs = []
		for key, abstract in enumerate(abstracts):
			word_dict = self.count_word_in_corpus(abstract)
			keys_dicts_for_abs.append((key, abstract))
		return keys_dicts_for_abs
