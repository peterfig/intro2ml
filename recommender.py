# Starter project for the college database machine learning exercise
#
# Here we've pulled out all the code from the notebook prototype and
# create a Python object called CollegeRecommender.
# The slow initialization tasks are completed in the initialization.
# Call doQuery to get recommendations.

from collegeconfig import query, dbfile_path, NUM_CLUSTERS, QUERY_SAT_ADD_MAX
import sqlite3
import pandas

from sklearn.cluster import KMeans
from sklearn.preprocessing import scale
from sklearn.decomposition import PCA


class CollegeRecommender(object):
	def __init__(self):
		df_joined = self._get_df_joined()
		df_pca = self._get_scaled_pca(df_joined)
		df_pca['KM_PCA_cluster'] = self._get_clusters(df_pca)
		# renumber the clusters to correspond to SAT scores
		# (lower cluster number = lower SAT score group)
		groups = df_pca.groupby('KM_PCA_cluster')
		cluster_number_map = groups.median().sort_values(by='sat_scaled').index
		d = { cluster_number_map[i]: i for i in range(NUM_CLUSTERS)}
		cluster_ord = df_pca.KM_PCA_cluster.map(lambda x: d[x])
		df_pca['cluster_ordinal'] = cluster_ord
		# Collect original data, scaled data, and cluster numbers
		df_out = pandas.concat([df_pca, df_joined], axis=1, join='inner')
		# Construct cluster lookup table
		out_groups = df_out[['cluster_ordinal','sat','AvgYrCostAcademic','earn10', 'completionRate']].groupby('cluster_ordinal')
		df_cluster_lookup = out_groups.median()
		# store data and lookup table
		self.df_joined = df_joined
		self.df_out = df_out
		self.df_cluster_lookup = df_cluster_lookup
		return

	def doQuery(self, data):
		""" respond to a recommendation request. input: data (dict) """
		# Find best cluster based on SAT score
		query_sat = data['verbal'] + data['math']
		query_cluster = (self.df_cluster_lookup.sat - query_sat).abs().argsort()[0]
		# Construct query
		c1 = self.df_out['cluster_ordinal'] == query_cluster
		c2 = self.df_out['AvgYrCostAcademic'] <= data['budget']
		c3 = self.df_out['sat'] <= query_sat + QUERY_SAT_ADD_MAX
		condition = c1 & c2 & c3
		# Pull data and report
		picks = self.df_out.loc[condition].sort_values(by='sat', ascending=False)[0:3].index
		df_response = self.df_joined.loc[picks,
			['INSTNM', 'type', 'NumStudents', 'AvgYrCostAcademic', 'sat', 'earn10']]
		return df_response.to_json(orient='records')

	def _get_df_joined(self):
		""" get raw college data from the db to a df, add computed columns """
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

	def _get_scaled_pca(self, df_joined):
		""" scale numerical data to normal centered at 0, apply PCA """
		dfc = df_joined[['sat', 'AvgYrCostAcademic', 'earn10', 'completionRate']].dropna()
		# scale
		column_rename = {0:'sat_scaled', 1:'cost', 2:'earn', 3:'gradrate'}
		dfscale = pandas.DataFrame(scale(dfc), index=dfc.index).rename(columns = column_rename)
		# PCA
		pca = PCA(n_components=4)
		pca_array = pca.fit_transform(dfscale[[u'sat_scaled', u'cost', u'earn', u'gradrate']])
		dfscale['PCA0'] = pca_array[:,0]
		dfscale['PCA1'] = pca_array[:,1]
		return dfscale

	def _get_clusters(self, dfscale):
		""" apply kmeans clustering to scaled data """
		km = KMeans(init='k-means++', n_clusters=NUM_CLUSTERS)
		clusters = km.fit_predict(dfscale[['PCA0','PCA1']])
		return clusters
