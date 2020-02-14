app_name = "NGD_APP"
# host of where you placed
# your pyspark server. If running
#locally, simply use local host
# and current port name.
host_name = "localhost"
xml_path = ""
port_name = "6379"
data_brick = 'com.databricks.spark.xml'
# tag for parsing the xml
row_tag = "MedlineCitation"
update_tag = "DeleteCitation"
sample_xml_path = "/Users/daniellin/Desktop/PubMed/update/sample_update.xml"
bulk_sample_path = "/Users/daniellin/Desktop/PubMed/update/"
# location for your sample xml for spark to load.
# you should just take one file from your bulk path,
# copy and paste them into the load_xml_path,
# and just leave it there. The purpose of this
# file is to let spark quickly build up
# the schema to load XML in bulks quickly.
load_xml_path = "/Users/daniellin/Desktop/sample/sample_for_loading2.xml"
# where your bulk XML files that you downloaded from pub med
# should reside in
bulk_path = "/Users/daniellin/Desktop/PubMed/"
# spark general configuration.
spark_mem_config = [('spark.executor.memory', '3g'), \
					('spark.app.name', 'XMLExtractor'), \
					('spark.executor.cores', '2'), \
					('spark.cores.max', '4'), \
					('spark.driver.memory','4g')]
