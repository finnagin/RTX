
def sample_workflow_example():
"""
	Name; sample_workflow_example
	Author: Daniel Lin
	Description:
		A sample function to demonstrate
		how to use my pyspark functions
		with normalized google distance.
"""
	# extract and create localized mesh dicts using pyspark
	df_entire = self.xml_extractor.get_entire_df()
	mesh_count = self.xml_extractor.count_each_mesh_occur(df_entire)
	uid_mesh, pmid_mesh_dict = self.xml_interface.data_frame_to_defaultdict(mesh_count)
	"""
		Do the normal process routine for weight_graph_with_normalized
		google_distance from ReasoningUtilities.py, except when
		calling QueryNCBIeUtils.multi_normalized_google_distance in the NormGoogleDistance.py,
		feed in pmid_mesh_dict into the second paramater
		as opposed to mesh_flags. so in NormGoogleDistance.get_ngd_for_all,
		in the calculated line:
			ngd = QueryNCBIeUtils.multi_normalized_google_distance(terms_combined, mesh_flags)
        	return ngd
        instead of passing mesh flags, do:
        	ngd = QueryNCBIeUtils.multi_normalized_google_distance(terms_combined, pmid_mesh_dict)
        	return ngd
	"""