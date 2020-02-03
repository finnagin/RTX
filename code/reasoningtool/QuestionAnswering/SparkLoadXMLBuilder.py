from pyspark import SparkContext
from config_file import data_brick
from config_file import row_tag
from config_file import load_xml_path
from config_file import bulk_path
from config_file import sample_xml_path
from config_file import bulk_sample_path
from config_file import update_tag

from SparkObjectBuilder import SparkObjBuilderInterface
from SparkObjectBuilder import SparkObjConcreteConstructor
from abc import ABCMeta, abstractmethod
"""
	Name: SparkLoadXMLBuilder
	Description:
		Abstract class for building
		spark object
"""
class SparkLoadXMLBuilder(metaclass=ABCMeta):
	def __init__(self):
		spark_constructor = SparkObjConcreteConstructor()
		interface = SparkObjBuilderInterface()
		self.product = interface.construct(spark_constructor)
	@abstractmethod
	def _add_sample_del_data(self):
		pass
	@abstractmethod
	def _add_sample_data(self):
		pass
	@abstractmethod
	def _add_entire_data(self):
		pass
"""
	Name: SparkLoadXMLConstructor
	Description:
		Concrete methods that implements
		all of the abstract methods above,
		and some other misc. methods.
"""
class SparkLoadXMLConstructor(SparkLoadXMLBuilder):
	"""
		Name: _add_sample_del_data
		Param: None
		Output: None
		Description:
			constructs a spark data frame from
			sample data.
	"""
	def _add_sample_del_data(self):
		print("+++++++ SAMPLING DAILY UPDATE SCHEMA ++++++++")
		df = self.product.read\
						 .format(data_brick)\
						 .options(rowTag=update_tag)\
						 .load(sample_xml_path)
		print("+++++++ FINISHED SAMPLING DAILY UPDATE SCHEMA ++++++++")
		return df
	"""
		Name: _add_del_data
		Param: None
		Output: None
		Description:
			loads an updated version of the
			data frame from spark.
	"""
	def _add_del_data(self, pre_comp_schema):
		print("+++++++ LOADING ENTIRE UPDATE XML SCHEMA +++++++")
		entire_df = self.product.read\
								.format(data_brick)\
								.options(rowTag=update_tag)\
								.load(bulk_sample_path, schema=pre_comp_schema)
		print("+++++++ FINISHED LOADING ENTIRE UPDATE XML SCHEMA+++++++")
		return entire_df
	"""
		Name: _add_entire_update_data
		Param: None
		Output: None
		Description:
			Loads entire update data frame from
			spark
	"""
	def _add_entire_update_data(self, pre_comp_schema):
		print("+++++++ LOADING ENTIRE UPDATE XML SCHEMA +++++++")
		entire_df = self.product.read\
								.format(data_brick)\
								.options(rowTag=row_tag)\
								.load(bulk_sample_path, schema=pre_comp_schema)
		print("+++++++ FINISHED LOADING ENTIRE UPDATE XML SCHEMA+++++++")
		return entire_df
	"""
		Name: _add_sample_data
		Param: None
		Output: None
		Description:
			Adds sample data frame to spark
			so that we can load entire folders of data
			from xml faster.
	"""
	def _add_sample_data(self):
		print("++++ SAMPLING XML FILE TO GEN SCHEMA +++++")
		df = self.product.read\
					.format(data_brick)\
					.options(rowTag=row_tag)\
					.load(load_xml_path).limit(10)
		print("++++++++ FINISHED SAMPLING ++++++++++++")
		return df
	"""
		Name: _add_entire_Data
		Param: None
		Output: None
		Description:
			Adds entire xml data to spark dataframe.
	"""
	def _add_entire_data(self, df, pre_comp_schema):
		print("++++ LOADING ENTIRE XML FILES IN FOLDER +++++")
		entire_df = self.product.read\
								.format(data_brick)\
					  			.options(rowTag=row_tag)\
					  			.load(bulk_path, schema=pre_comp_schema)
		print("++++ FINISHED ENTIRE XML FILES IN FOLDER +++++")
		return entire_df
	"""
		Name: get_product
		Param: None
		Output: None
		Description:
			returns the product object
			after building it through the builder
			object class.
	"""
	def get_product(self):
		return self.product
"""
	Name: SparkLoadXMLInterface
	Description:
		Concrete interface class
		that returns the object
		status that we want.
"""
class SparkLoadXMLInterface:
	def __init__(self):
		self.builder = None
	"""
		Name: construct_reg
		Param:
			conc_builder: SparkLoadXMLConstructor
			schema_ctx: Schema context generated from spark
			df: spark data frame
		Output:
			df: spark data frame
		Description:
			constructs a spark data frame
			from regular xml files.
	"""
	def construct_reg(self, conc_builder, schema_ctx, df):
		self.builder = conc_builder
		return self.builder._add_entire_data(df, schema_ctx)
	"""
		Name: construct_sample
		Param:
			conc_builder: SparkLoadXMlConstructor
		Output:
			df: spark data frame
		Description:
			returns a sample data frame
			from spark.
	"""
	def construct_sample(self, conc_builder):
		self.builder=conc_builder
		return self.builder._add_sample_data()
	"""
		Name: construct_sample_del
		Param:
			conc_builder: SparkLoadXMlConstructor
		Output:
			df: spark data frame
		Description:
			returns a spark data frame
			with sample deleted data
	"""
	def construct_sample_del(self, conc_builder):
		self.builder = conc_builder
		return self.builder._add_sample_del_data()
	"""
		Name: construct_entire_del
		Param:
			conc_builder: SparkLoadXMlConstructor
			schema_ctx: Schema sample data
		Output:
			df: spark data frame
		Description:
			returns a spark data frame
			for all of the data that should be
			deleted.
	"""
	def construct_entire_del(self, conc_builder, schema_ctx):
		return conc_builder._add_del_data(schema_ctx)
	"""
		Name: construct_sample
		Param:
			conc_builder: SparkLoadXMlConstructor
			schema_ctx: Schema sample data
		Output:
			df: spark data frame
		Description:
			returns a dataframe for the entire
			updated xml data
	"""
	def construct_entire_update(self, conc_builder, schema_ctx):
		return conc_builder._add_entire_update_data(schema_ctx)
