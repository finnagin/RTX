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
"""
	Name: SparkObjectConstruct
	Description:
		Abstract object for spark
		object construction
"""
class SparkObjectConstruct(metaclass=ABCMeta):
	def __init__(self):
		self.product = SparkConf()
	@abstractmethod
	def _add_conf_memory(self):
		pass
"""
	Name: SparkObjConcreteConstructor
	Description:
		Concrete methods
		for constructing spark objects.
"""
class SparkObjConcreteConstructor(SparkObjectConstruct):
	"""
		Name: _add_conf_memory
		Input: None
		Output: None
		Description:
			adds memory configurations to
			the spark object
	"""
	def _add_conf_memory(self):
		self.product.setAll(spark_mem_config)
	"""
		Name: _add_jars_memory
		Input: None
		Output: None
		Description:
			Adds jar configuration to
			spark object.
	"""
	def _add_jars_conf(self):
		# add jar dependencies.
		self.product.set('spark.jars.packages',\
						 'com.databricks:spark-xml_2.11:0.6.0')
	"""
		Name: get_product
		Input: None
		Output: None
		Description:
			returns the object constructed.
	"""
	def get_product(self):
		return self.product
"""
	Name: SparkObjBuilderInterface
	Description:
		Concrete object interface
		function for our spark object.
"""
class SparkObjBuilderInterface:
	def __init__(self):
		self.builder = None
	"""
		Name: construct
		Input:
			conc_builder: SparkObjConcreteConstructor
		Output: None
		Description:
			concrete spark object interface
			builder.
	"""
	def construct(self, conc_builder):
		self.builder=conc_builder
		self.builder._add_conf_memory()
		self.builder._add_jars_conf()
		spark_conf = self.builder.get_product()
		print("+++++++GENERATING SPARK CONTEXT ++++++++++")
		spark = SparkSession.builder\
						   .config(conf = spark_conf)\
						   .getOrCreate()
		print("+++++++FINISHED GENERATING SPARK CONTEXT ++++++++++")
		return spark
