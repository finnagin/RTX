__author__ = 'Daniel Lin '
__copyright__ = 'Oregon State University'
__credits__ = ['Daniel Lin']
__license__ = 'MIT'
__version__ = '0.1.0'
__maintainer__ = 'Daniel Lin'
__email__ = 'danieltzulin@gmail.com'
__status__ = 'Prototype'
import sys
sys.path.append(".")

from SparkObjectBuilder  import SparkObjConcreteConstructor
from SparkObjectBuilder  import SparkObjBuilderInterface
from SparkLoadXMLBuilder import SparkLoadXMLInterface
from SparkLoadXMLBuilder import SparkLoadXMLConstructor

from pyspark.sql.functions import explode
from pyspark.sql.functions import col
from pyspark.sql.functions import arrays_zip
from pyspark.sql.functions import collect_list
from pyspark.sql.functions import array_contains
from pyspark.sql.functions import size
from pyspark.sql.functions import to_json
from pyspark.sql.functions import struct
from pyspark.sql.functions import array
from pyspark.sql.functions import when

from multiprocessing import Manager
from multiprocessing import Pool
from multiprocessing import cpu_count
from collections import defaultdict

from math import floor
from json import dumps
"""
	Name: XMLInterface
	Description:
		XML extractor class.
"""
class XMLInterface:
	def __init__(self):
		self.mesh_uid_dict_par = Manager().dict()
		self.mesh_occur_dict_par = Manager().dict()
		self.mesh_occur_dict = defaultdict()
		self.mesh_uid_dict = defaultdict()
	"""
		Name: XML_main
		Input:
			interface:SparkLoadXMLInterface
		Output:
			uid_mesh: uid-mesh dict
			pmid_mesh_dict: pmid_mesh_dict
		Description:
			Converts df to python dictionary.
	"""
	def XML_main(self, interface):
		df_sample = interface.construct_sample(self.conc_constructor)
		sample_schema = df_sample.schema
		df_entire = interface.construct_reg(self.conc_constructor, \
											sample_schema, \
											df_sample)
		mesh_count = self.count_each_mesh_occur(df_entire)
		uid_mesh, pmid_mesh_dict = self.data_frame_to_defaultdict(mesh_count)
		return uid_mesh, pmid_mesh_dict

	"""
		Name: insert_into_dict
		Input:
			frame: spark column data frame
		Output: None
		Description:
			insert spark column data frame into python dictionary
	"""
	def insert_into_dict(self, frame):
		mesh, uid = self.get_mesh_uid(frame)
		pmid_list, count = self.get_pmid_list_count(frame)
		if mesh or uid:
			pmid_list_cnt = (pmid_list, count)
			self.mesh_uid_dict_par[uid[1:]] = mesh
			self.mesh_occur_dict_par[mesh] = pmid_list_cnt
	"""
		Name: slice_dataframe
		Input:
			data_frame: lists of data frames
			n: number of slices
		Output: None
		Description:
			slice data frame in order
			to be processed by multicore
			processing.
	"""
	def slice_dataframe(self, data_frame, n):
		k,m = divmod(len(data_frame), n)
		return [a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]
	"""
		Name: data_frame_to_defaultdict
		Input:
			data_frame: spark data frame
		Output:
			uid_mesh: uid-mesh dict
			pmid_mesh_dict: pmid_mesh_dict
		Description:
			main function to convert spark dataframe
			to python dictionaries. Used by XML_main
			to convert pyspark data frame to defaultdict.
	"""
	def data_frame_to_defaultdict(self, data_frame):
		print("++++++ Loading Data into defaultdict ++++++++++")
		"""
			Using multiprocessing to speed up
			insertion operation into dictionary
			if dataframe contains more than
			100,000 items. Else, just process
			the dataframes sequentially. For
			dataframes less than 100K, the processing
			time is less than a second. It doesn't
			make sense to pay the cost of setting
			up multiprocessing when the sequential
			processing time is acceptable already.
		"""
		parallel_threshold = 100000
		if len(data_frame) >= parallel_threshold:
			cpu_cnt = cpu_count()
			chunk  = int(len(data_frame) / cpu_cnt)+1
			p = Pool(cpu_cnt)
			chunked_dataframe = self.slice_dataframe(data_frame, chunk)
			p.map(self.insert_into_dict, chunked_dataframe)
			p.close()
			return (self.mesh_uid_dict, self.mesh_occur_dict)
		for row in data_frame:
			mesh, uid = self.get_mesh_uid(row)
			pmid_list, count = self.get_pmid_list_count(row)
			if mesh or uid:
				pmid_list_cnt = (pmid_list, count)
				self.mesh_uid_dict[uid[1:]] = mesh
				self.mesh_occur_dict[mesh] = pmid_list_cnt
		print("++++++ Finished Loading Data Into defaultdict ++++++++++")
		return (self.mesh_uid_dict, self.mesh_occur_dict)

	def get_mesh_uid(self, frame):
		return (frame["Mesh"], frame["UIDs"])
	def get_pmid_list_count(self, frame):
		return (frame["PMID_List"], frame["MeshOccurCount"])
"""
	Name: Spark_XML_ETL
	Description:
		Utility functions class for performing
		Extract Load Transform (ETL)
		using Spark.
"""
class Spark_XML_ETL:
	def __init__(self):
		self.conc_constructor = SparkLoadXMLConstructor()
		self.interface = SparkLoadXMLInterface()
	"""
		Name: updated_citations
		Input: None
		Output:
			pyspark data frame
			that includes all of the updated
			citations
		Description:
			Produces a dataframe that includes all of the
			updated citations from PubMed.
	"""
	def updated_citations(self):
		# read all of the update baseline xmls
		update_sample_dfs = self.interface.construct_sample_update(self.conc_constructor)
		updated_sample_schema = update_sample_dfs.schema
		return self.interface.construct_entire_update(self.conc_constructor,\
													  updated_sample_schema)
	"""
		Name: del_existing_citations
		Input: None
		Output:
			df: pyspark data frame
			update_df: data frame containing updated xml data
		Description:
			Filters out data frame that are not to be deleted.
	"""
	def del_existing_citations(self, df, update_df):
		citations_to_del = update_df.select(update_df["DeleteCitation"])
		return df.filter(df["PMID"] != citations_to_del["PMID"])
	"""
		Name: update_existing_citations
		Input:
			df: pyspark data frame
			update_df: data frame with updated data
		Output:
			updated data frame with updated
			citation data
		Description:
			update citation dataframe df
			with new citations data frame from update_df
	"""
	def update_existing_citations(self, df, update_df):
		mesh_val = "MeshHeadingList.MeshHeading.DescriptorName._VALUE"
		col_to_ignore = "DeletionSets"
		non_dels = update_df.select([c for c in df.columns if c != col_to_ignore])
		return df.withColumn(mesh_val,
								when(
								 	col("PMID") == non_dels["PMID"],
								 	non_dels[mesh_val]
								).otherwise(col(mesh_val))
							)
	# wrapper function to construct pyspark data frame
	def df_gen(self, schema, df):
		return self.interface.construct_reg(schema, df)
	"""
		Gen a schema of the data
		and load them into spark,
		else spark is going to take
		a long time processing the XMLs
	"""
	def gen_schema(self):
		return self.interface.construct_sample(self.conc_constructor)
	"""
		Name: count_each_mesh_occur
		Input:
			df_entire: data frame containing entire xml data
		Output:
			final pyspark data frame with the right
			column name and shape
		Description:
			massages the pyspark data frame df_entire
			into column names that makes sense
			and correct dataframe shape. Then,
			it counts how many times each
			mesh_uids and pmids occur in the data frame,
			and finally produces the data frame
			with that count as the column.
	"""
	def count_each_mesh_occur(self, df_entire):
		mesh_heading_descriptor_val = "MeshHeadingList.MeshHeading.DescriptorName._VALUE"
		mesh_uid = "MeshHeadingList.MeshHeading.DescriptorName._UI"
		pmid_mesh = df_entire.select(col("PMID._VALUE").alias("PMID"), \
									 col(mesh_heading_descriptor_val).alias("MeshVals"),
									 col(mesh_uid).alias("MeshUIDs")
								    )
		zipped_val = self.zip_meshvals_meshuids(pmid_mesh)
		pmid_mesh_uids = self.get_pmid_mesh_uids(zipped_val)
		group_pmid_meshuids = self.get_group_pmid_meshuid_df(pmid_mesh_uids)
		return self.get_final_dataframe(group_pmid_meshuids).collect()
	# wrapper function for constructing a data frame
	# from sample data
	def gen_sample_schema(self):
		return self.interface.construct_sample(self.conc_constructor)
	"""
		Name: get_entire_df
		Input: None
		Output:
			dataframe with the entire loaded
			xml
		Description:
			Constructs a dataframe from the
			entire xml files from pubmed
	"""
	def get_entire_df(self):
		df_sample = self.gen_sample_schema()
		sample_schema= df_sample.schema
		return self.interface.construct_reg(self.conc_constructor, \
											sample_schema, \
											self.df_sample)
	"""
		Name: get_dels_df
		Input: None
		Output:
			data frame that contains the entire
			pubmeds data to be deleted
		Description:
			creates a data frame for all of the
			citations that need to be deleted
	"""
	def get_dels_df(self):
		update_df_samp = self.interface.construct_sample_del(self.conc_constructor)
		#update_df_samp.printSchema()
		update_schema = update_df_samp.schema
		return self.get_entire_update_df(update_schema)
	# wrapper function for constructing entire deletion data frame
	def get_entire_update_df(self, input_schema):
		return self.interface.construct_entire_del(self.conc_constructor, input_schema)
	# wrapper function for constructing entire dataframes with data
	# that needs to be updated.
	def get_update_df(self, schema):
		return self.interface.construct_entire_update(self.conc_constructor, schema)
	# wrapper function for pyspark arrays_zip;
	# performs python-like zip on two columns, where each
	# value in the column is an array of data.
	def zip_meshvals_meshuids(self, df):
		return df.withColumn('MeshAndUIDs', arrays_zip("MeshVals", "MeshUIDs"))
	# wrapper function for pyspark that generates pmid_mesh_uids from data
	def get_pmid_mesh_uids(self, df):
		return df.select(col("PMID"),
						 explode("MeshAndUIDs").alias("Mesh_UID_Pair"))
	# groups PMID and PMID_List together ; massages data frame function
	def get_group_pmid_meshuid_df(self, df):
		return df.groupBy("Mesh_UID_Pair")\
				 .agg(collect_list('PMID').alias("PMID_List"))
	# function that massages the data to have correct column names.
	def get_final_dataframe(self, df):
		return df.withColumn("Mesh", col("Mesh_UID_Pair.MeshVals"))\
				 .withColumn("UIDs", col("Mesh_UID_Pair.MeshUIDs"))\
				 .select(col("Mesh"), col("UIDs"), col("PMID_List"))\
				 .withColumn("MeshOccurCount", size(col("PMID_List")))