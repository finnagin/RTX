from pyspark import SparkContext
from config_file import data_brick
from config_file import row_tag
from config_file import load_xml_path
from config_file import bulk_path

from SparkObjectBuilder import SparkObjBuilderInterface
from SparkObjectBuilder import SparkObjConcreteConstructor

class SparkLoadXMLBuilder(metaclass=abc.ABCMeta):
	def __init__(self):
		spark_constructor = SparkObjConcreteConstructor()
		interface = SparkObjBuilderInterface()
		# our dataframe
		self.product = interface.construct(spark_constructor)
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

class SparkLoadXMLConstructor(SparkObjectConstruct):
	def _add_format(self):
		self.product.format(data_brick)
	def _add_options(self):
		self.product.options(rowTag=row_tag)
	def _add_load(self, schema_context):
		self.product.load(bulk_path, schema=schema_context)
	def _add_load_sample(self):
		self.product.load(bulk_path)
	def _add_sample(self):
		self.product.load(load_xml_path).limit(10)
	def gen_schema(self):
		self.product.schema
	def get_product(self):
		return self.product

class SparkLoadXMLInterface:
	def __init__(self):
		self.builder = None
	def construct_reg(self, conc_builder, schema):
		self.builder=conc_builder
		self.builder._add_format()
		self.builder._add_options()
		self.builder._add_load(schema)
		return conc_builder.get_product()
	def construct_sample(self, conc_builder):
		self.builder=conc_builder
		self.builder._add_format()
		self.builder._add_options()
		self.builder._add_load_sample()
		self.builder._add_sample()
		self.builder.gen_schema()
		return conc_builder.get_product()