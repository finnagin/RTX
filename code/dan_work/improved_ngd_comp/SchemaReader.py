__author__ = 'Daniel Lin '
__copyright__ = 'Oregon State University'
__credits__ = ['Daniel Lin']
__license__ = 'MIT'
__version__ = '0.1.0'
__maintainer__ = 'Daniel Lin'
__email__ = 'danieltzulin@gmail.com'
__status__ = 'Prototype'
import json

from SchemaLoadXMLBuilder import SparkLoadXMLInterface
from SchemaLoadXMLBuilder import SparkLoadXMLConstructor
"""
	Name: SchemaReaderTool
	Desc:
		Handy tool to read in large
		XML schemas efficiently by
		first sampling a small
		part of the XML file and
		generate the schema
		based on the sample
"""
class SchemaReaderTool:
	"""
		Gen a schema of the data
		and load them into spark,
		else spark is going to take
		a long time processing the XMLs
	"""
	def gen_schema(self, path):
		#schema = self.spark\
		#		.read.format('com.databricks.spark.xml')\
		#		.options(rowTag="MedlineCitation")\
		#		.load("/Users/daniellin/Desktop/PubMed/pubmed19n0009.xml").limit(5)
		conc_constructor = SparkLoadXMLConstructor()
		interface = SparkLoadXMLInterface()
		return interface.construct_sample(conc_constructor)
