import time
import cypher

from networkx import edges,nodes
from matplotlib import pyplot as plt
from ReasoningUtilities import defaults
from ReasoningUtilities import connection
from ReasoningUtilities import get_graph
"""
	Name: bench_harness
	input:
		iterations:int
	output:
		function: test_google_benchmark
	description:
		This is the decorator function
		used as our testing harness
"""
def bench_harness(iterations):
	# decorator function
	def benchmark_timer(function, *args, **kwargs):
		file_name = kwargs['file_name']
		fun_name = kwargs['fun_name']
		file_path = './benchmark_res/%s.txt' % (file_name)
		f = open(file_name, 'a')
		ts = time.time()
		print("Testing function %s" % (fun_name))
		function()
		te = time.time()
		print("Testing Complete for %s" % (fun_name))
		run_time = te-ts
		terms_runtime_data = "%i\t%f\n" % (num_terms, float(run_time))
		f.write(terms_runtime_data)
		f.close()
		return function
	return bench_start