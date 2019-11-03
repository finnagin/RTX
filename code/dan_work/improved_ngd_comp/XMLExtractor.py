from SchemaReader import SchemaReaderTool
from SchemaLoadXMLBuilder import SparkLoadXMLInterface
from SchemaLoadXMLBuilder import SparkLoadXMLConstructor
from config_file import load_xml_path

from pyspark.sql import SQLContext
from config_file import xml_path

class XMLExtractor:
	def spark_schema(self):
		schema_tool = SchemaReaderTool()
		return schema_tool.gen_schema(load_xml_path)
	def df_gen(self):
		schema = self.spark_schema()
		conc_constructor = SparkLoadXMLConstructor()
		interface = SparkLoadXMLInterface()
		interface.construct_reg(schema)
		return conc_constructor.get_product()
