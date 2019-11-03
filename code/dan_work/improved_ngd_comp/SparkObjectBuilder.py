from pyspark.sql import SparkSession
from config_file import app_name
from config_file import host_name
from config_file import port_name
from config_file import spark_redis_host
from config_file import spark_redis_port

class SparkObjectConstruct(metaclass=abc.ABCMeta):
	def __init__(self):
		self.product = SparkSession()
	@abc.abstract_method
	def _add_builder(self):
		pass
	@abc.abstract_method
	def _add_appname(self):
		pass
	@abc.abstract_method
	def _add_host_conf(self):
		pass
	@abc.abstract_method
	def _add_port_conf(self):
		pass

class SparkObjConcreteConstructor(SparkObjectConstruct):
	def _add_builder(self):
		self.product.builder
	def _add_appname(self):
		self.product.appName(app_name)
	def _add_host_conf(self):
		self.product.config(spark_redis_host, host_name)
	def _add_port_conf(self):
		self.product.config(spark_redis_port, port_name)
	def get_product(self):
		return self.product

class SparkObjBuilderInterface:
	def __init__(self):
		self.builder = None
	def construct(self, conc_builder):
		self.builder=conc_builder
		self.builder._add_builder()
		self.builder._add_appname()
		self.builder._add_host_conf()
		self.builder._add_port_conf()
		return conc_builder.get_product()