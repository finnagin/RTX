from unittest import main
from unittest import TestCase
from config_file import spark_mem_config
import json

from SparkObjectBuilder import SparkObjConcreteConstructor
from SparkObjectBuilder import SparkObjBuilderInterface
from SparkLoadXMLBuilder import SparkLoadXMLInterface
from SparkLoadXMLBuilder import SparkLoadXMLConstructor
"""
	Name: SparkObjectTest
	Description:
		This class consists of
		unit tests written to test
		the  classes in SparkObjectBuilder.py.
"""
class SparkObjectTest(TestCase):
	def setUp(self):
		self.spark_obj_const = SparkObjConcreteConstructor()
		self.spark_interface = SparkObjBuilderInterface()
	"""
		Name: test_spark_object_constructor
		Param: None
		Output: None
		Description:
			Tests whether the SparkConf object
			is constructed correctly. Once
			the object is created, we use
			getConf().getAll() to get
			the configuration of the SparkConf
			in json, and we loop through the
			json to see if everything in
			spark_mem_config is inside the
			newly constructed SparkConf object.
	"""
	def test_spark_object_constructor(self):
		spark = self.spark_interface.construct(self.spark_obj_const)
		spark_conf = spark.sparkContext.getConf().getAll()
		expected_confs = spark_mem_config

		for expected_conf in expected_confs:
			is_inside = expected_conf in spark_conf
			self.assertEqual(is_inside, True)
		spark.sparkContext.stop()
	"""
		Name: test_sample_xml
		Param: None
		Output: None
		Description:
			Tests whether we can create
			a sample xml loader using
			SparkSession and run without
			errors. If there function
			does not throw any errors,
			this means that the function
			can successfuly construct an xml
			sample.
	"""
	def test_sample_xml(self):
		spark_xml_constructor = SparkLoadXMLConstructor()
		spark_xml_const_interface = SparkLoadXMLInterface()
		df_sample = spark_xml_const_interface.construct_sample(spark_xml_constructor)
	"""
		Name: test_load_xml_bulk
		Param: None
		Output: None
		Description:
			Tests whether the xml loader
			can load a bulk of xml files.
			The size tested is a folder
			of xml files with a size
			of 1GB.
	"""
	def test_load_xml_bulk(self):
		spark_xml_constructor = SparkLoadXMLConstructor()
		spark_xml_const_interface = SparkLoadXMLInterface()
		df_sample = spark_xml_const_interface.construct_sample(spark_xml_constructor)
		sample_schema= df_sample.schema
		df_entire = spark_xml_const_interface.construct_reg(spark_xml_constructor, \
															sample_schema, \
															df_sample)
		# sanity check to make sure the data is in pyspark.sql
		sample_test_case = "Laser lingual tonsillotomy."
		expeted_res = "Hungary"
		res = df_entire.filter(df_entire["Article.ArticleTitle"] == sample_test_case)
		row_data = res.select("MedlineJournalInfo").collect()
		collected_val = row_data[0]["MedlineJournalInfo"]["Country"]
		# sanity test to see if the dict is built
		self.assertEqual(collected_val, expeted_res)

if __name__ == '__main__':
	main()