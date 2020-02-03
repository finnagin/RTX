from unittest import TestCase
from unittest import main

from XMLExtractor 		 import Spark_XML_ETL
from XMLExtractor 		 import XMLInterface
from SparkObjectBuilder  import SparkObjConcreteConstructor
from SparkObjectBuilder  import SparkObjBuilderInterface
from SparkLoadXMLBuilder import SparkLoadXMLInterface
from SparkLoadXMLBuilder import SparkLoadXMLConstructor
"""
	Name: XMLExtractorTest
	Description:
		Testing class for testing functions inside
		XMLExtractor.py
"""
class XMLExtractorTest(TestCase):
	def setUp(self):
		self.xml_extractor = Spark_XML_ETL()
		self.xml_interface = XMLInterface()
	"""
		Name: test_xml_mesh_dict
		Param: None
		Output: None
		Description:
			Tests whether our spark dataframe
			can correctly load the entire
			data frame from xml to python dict
	"""
	def test_xml_mesh_dict(self):
		df_entire = self.xml_extractor.get_entire_df()
		mesh_count = self.xml_extractor.count_each_mesh_occur(df_entire)
		uid_mesh, pmid_mesh_dict = self.xml_interface.data_frame_to_defaultdict(mesh_count)
		# sanity test: make sure sure a randomly
		# picked drug "Thebaine" is inside the dict
		self.assertEqual('Thebaine', uid_mesh['013797'])
	"""
		Name: test_read_entire_schema
		Param: None
		Output: None
		Description:
			Tests to see of spark can
			read entire schema
	"""
	def test_read_entire_schema(self):
		df_entire = self.xml_extractor.get_entire_df()
		print("My entire schema")
		print(df_entire.printSchema())
	"""
		Name: test_read_update_schema
		Param: None
		Output: None
		Description:
			Tests to see if spark can delete and update
			dataframe base on new schema data
	"""
	def test_read_update_df(self):
		updated_del_df = self.xml_extractor.get_dels_df()
		df_sample = self.xml_extractor.gen_sample_schema()
		df_sample_schema = df_sample.schema
		to_update_df = self.xml_extractor.get_update_df(df_sample_schema)
		print("My entire update schema")
		updated_del_df.printSchema()
		to_update_df.printSchema()
	"""
		Name: test_filter_citations_fun
		Param: None
		Output: None
		Description:
			Tests whether the function can filter information
			from the schema during update.
	"""
	def test_filter_citations_fun(self):
		df_entire = self.xml_extractor.get_entire_df()
		df_of_pmids_to_del = self.xml_extractor.get_dels_df()
		results_omitted = df_of_pmids_to_del.collect()
		df_with_omitted_pmids = self.xml_extractor.del_existing_citations(df_entire, \
																		  df_of_pmids_to_del
																		 )
		df_with_omitted_pmids = df_with_omitted_pmids.collect()
		for ommitted_result in results_omitted:
			is_res_ommitted = ommitted_result in df_with_omitted_pmids
			self.assertEqual(False, is_res_ommitted)
if __name__ == '__main__':
	main()