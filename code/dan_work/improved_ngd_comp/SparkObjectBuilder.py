import sys
sys.path.append('.')

from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from config_file import app_name
from config_file import host_name
from config_file import port_name
from config_file import spark_mem_config
from config_file import spark_redis_jar
from abc import ABCMeta, abstractmethod

class SparkObjectConstruct(metaclass=ABCMeta):
	def __init__(self):
		self.product = SparkConf()
	#@abstractmethod
	#def _add_host_conf(self):
	#	pass
	#@abstractmethod
	#def _add_port_conf(self):
	#	pass
	@abstractmethod
	def _add_conf_memory(self):
		pass

class SparkObjConcreteConstructor(SparkObjectConstruct):
	#def _add_host_conf(self):
	#	self.product.set(spark_redis_host, host_name)
	#def _add_port_conf(self):
	#	self.product.set(spark_redis_port, port_name)
	def _add_conf_memory(self):
		self.product.setAll(spark_mem_config)
	def _add_jars_conf(self):
		# add jar dependencies.
		self.product.set('spark.jars.packages',\
						 'com.databricks:spark-xml_2.11:0.6.0')
		#self.product.set('spark.jars', spark_redis_jar)
	def get_product(self):
		return self.product

class SparkObjBuilderInterface:
	def __init__(self):
		self.builder = None

	def construct(self, conc_builder):
		self.builder=conc_builder
		self.builder._add_conf_memory()
		#self.builder._add_host_conf()
		#self.builder._add_port_conf()
		self.builder._add_jars_conf()
		spark_conf = self.builder.get_product()
		print("+++++++GENERATING SPARK CONTEXT ++++++++++")
		spark = SparkSession.builder\
						   .config(conf = spark_conf)\
						   .getOrCreate()
		print("+++++++FINISHED GENERATING SPARK CONTEXT ++++++++++")
		return spark
