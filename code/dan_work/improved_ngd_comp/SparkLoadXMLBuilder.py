from pyspark import SparkContext
from config_file import data_brick
from config_file import row_tag
from config_file import load_xml_path
from config_file import bulk_path

from SparkObjectBuilder import SparkObjBuilderInterface
from SparkObjectBuilder import SparkObjConcreteConstructor
from abc import ABCMeta, abstractmethod

class SparkLoadXMLBuilder(metaclass=ABCMeta):
	def __init__(self):
		spark_constructor = SparkObjConcreteConstructor()
		interface = SparkObjBuilderInterface()
		self.product = interface.construct(spark_constructor)
	@abstractmethod
	def _add_sample_update_data(self):
		pass
	@abstractmethod
	def _add_sample_data(self):
		pass
	@abstractmethod
	def _add_entire_data(self):
		pass

class SparkLoadXMLConstructor(SparkLoadXMLBuilder):
	def _add_sample_update_data(self):
		print("+++++++ SAMPLING DAILY UPDATE SCHEMA ++++++++")
		df = self.product.read\
						 .format(data_brick)\
						 .load(sample_xml_path).limit(10)
		print("+++++++ FINISHED SAMPLING DAILY UPDATE SCHEMA ++++++++")
		return df
	def _add_update_data(self, pre_comp_schema):
		print("+++++++ LOADING ENTIRE UPDATE XML SCHEMA +++++++")
		entire_df = self.product.read\
								.format(data_brick)\
								.load(bulk_sample_path, schema=pre_comp_schema)
		print("+++++++ FINISHED LOADING ENTIRE UPDATE XML SCHEMA+++++++")
		return entire_df

	def _add_sample_data(self):
		print("++++ SAMPLING XML FILE TO GEN SCHEMA +++++")
		df = self.product.read\
					.format(data_brick)\
					.options(rowTag=row_tag)\
					.load(load_xml_path).limit(10)
		print("++++++++ FINISHED SAMPLING ++++++++++++")
		return df
	def _add_entire_data(self, df, pre_comp_schema):
		print("++++ LOADING ENTIRE XML FILES IN FOLDER +++++")
		entire_df = self.product.read\
								.format(data_brick)\
					  			.options(rowTag=row_tag)\
					  			.load(bulk_path, schema=pre_comp_schema)
		print("++++ FINISHED ENTIRE XML FILES IN FOLDER +++++")
		return entire_df
	def get_product(self):
		return self.product

class SparkLoadXMLInterface:
	def __init__(self):
		self.builder = None
	def construct_reg(self, conc_builder, schema_ctx, df):
		self.builder = conc_builder
		return self.builder._add_entire_data(df, schema_ctx)

	def construct_sample(self, conc_builder):
		self.builder=conc_builder
		return self.builder._add_sample_data()

	def construct_sample_update(self, conc_builder):
		self.builder = conc_builder
		return self.builder._add_sample_update_data()

	def construct_entire_update(self, conc_builder, schema_ctx)
		return conc_builder._add_update_data(schema_ctx)

