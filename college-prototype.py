# Starter project for the college database machine learning exercise
#
# Here we've pulled out all the code from the notebook prototype and
# have it running as a script.  This is just a starting point, as it is not
# very useful except to collect the code in one place and verify it is operational.
#
# The next step would be to refactor the script into a series of functions, and,
# implement a RESTful service using Django.  You'll want to load and process the data
# during the service's init phase.  You only need to do this once during the init phase.
# Then respond to queries by using the lookups
# you've created.

import argparse
import json
from collegeconfig import query, dbfile_path, NUM_CLUSTERS, QUERY_SAT_ADD_MAX
import sqlite3
import pandas

def get_df_joined():
	conn = sqlite3.connect(dbfile_path)
	print "reading 2013 data.."
	df2013 = pandas.read_sql(query.format(2013), conn)
	print "reading 2011 data.."
	df2011 = pandas.read_sql(query.format(2011), conn)
	print "joining data.."
	df2011.set_index(['UNITID'], inplace=True)  
	df2013.set_index(['UNITID'], inplace=True)
	df2011['earn10'] = pandas.to_numeric(df2011['medEarn10yrs'], errors='coerce')
	df2013['sat'] = df2013['Math'] + df2013['Verbal']
	dfearn = df2011['earn10'].dropna()
	df_joined = pandas.concat([df2013, dfearn], axis=1, join='inner')
	print "done."
	return df_joined
	
if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("infile", help="json input file")
	args = parser.parse_args()
	with open(args.infile) as data_file:    
		data = json.load(data_file)

	print "Got input:", data
	df_joined = get_df_joined()
	
	# Let's collect our code from the prototype notebook.
	# We can refactor it later.
	dfc = df_joined[['sat', 'AvgYrCostAcademic', 'earn10', 'completionRate']].dropna()
	
	# scale
	from sklearn.preprocessing import scale
	column_rename = {0:'sat_scaled', 1:'cost', 2:'earn', 3:'gradrate'}
	dfscale = pandas.DataFrame(scale(dfc), index=dfc.index).rename(columns = column_rename)
	
	# PCA
	from sklearn.decomposition import PCA
	pca = PCA(n_components=4)
	pca_array = pca.fit_transform(dfscale[[u'sat_scaled', u'cost', u'earn', u'gradrate']])
	dfscale['PCA0'] = pca_array[:,0]
	dfscale['PCA1'] = pca_array[:,1]
	
	# cluster
	from sklearn.cluster import KMeans
	km = KMeans(init='k-means++', n_clusters=NUM_CLUSTERS)
	km.fit(dfscale[['PCA0','PCA1']])
	dfscale['KM_PCA_cluster'] = km.predict(dfscale[['PCA0','PCA1']])
	
	# renumber the clusters to correspond to SAT scores 
	# (lower cluster number = lower SAT score group)
	groups = dfscale.groupby('KM_PCA_cluster')
	cluster_number_map = groups.median().sort_values(by='sat_scaled').index 
	d = { cluster_number_map[i]: i for i in range(NUM_CLUSTERS)}
	cluster_ord = dfscale.KM_PCA_cluster.map(lambda x: d[x])
	dfscale['cluster_ordinal'] = cluster_ord
	
	# Collect original data, scaled data, and cluster numbers
	df_out = pandas.concat([dfscale, df_joined], axis=1, join='inner')
	
	# Construct cluster lookup table
	out_groups = df_out[['cluster_ordinal','sat','AvgYrCostAcademic','earn10', 'completionRate']].groupby('cluster_ordinal')
	df_cluster_lookup = out_groups.median()
	
	# Find best cluster based on SAT score
	query_sat = data['verbal'] + data['math']
	query_cluster = (df_cluster_lookup.sat - query_sat).abs().argsort()[0]
	
	# Construct query
	c1 = df_out['cluster_ordinal'] == query_cluster
	c2 = df_out['AvgYrCostAcademic'] <= data['budget']
	c3 = df_out['sat'] <= query_sat + QUERY_SAT_ADD_MAX
	condition = c1 & c2 & c3
	
	# Pull data and report
	picks = df_out.loc[condition].sort_values(by='sat', ascending=False)[0:3].index
	df_response = df_joined.loc[picks, 
		['INSTNM', 'type', 'NumStudents', 'AvgYrCostAcademic', 'sat', 'earn10']]
	print df_response.to_json(orient='records')
	