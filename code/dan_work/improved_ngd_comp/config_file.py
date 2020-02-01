app_name = "NGD_APP"
host_name = "localhost"
xml_path = ""
port_name = "6379"
data_brick = 'com.databricks.spark.xml'
row_tag = "MedlineCitation"
update_tag = "DeleteCitation"
sample_xml_path = "/Users/daniellin/Desktop/PubMed/update/sample_update.xml"
bulk_sample_path = "/Users/daniellin/Desktop/PubMed/update/"
# location for your sample xml for spark to load
load_xml_path = "/Users/daniellin/Desktop/sample/sample_for_loading2.xml"
# where your bulk XML files are
bulk_path = "/Users/daniellin/Desktop/PubMed/"
# spark general config
spark_mem_config = [('spark.executor.memory', '3g'), \
					('spark.app.name', 'XMLExtractor'), \
					('spark.executor.cores', '2'), \
					('spark.cores.max', '4'), \
					('spark.driver.memory','4g')]
# spark-redis connector jar path
spark_redis_jar = '/Users/daniellin/Desktop/OSU_Job/RTX/code/dan_work/spark-redis/target/spark-redis-2.4.1-SNAPSHOT-jar-with-dependencies.jar'