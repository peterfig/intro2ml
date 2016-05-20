import argparse
import json
from collegeconfig import query
import sqlite3
import pandas

def get_df_joined():
	conn = sqlite3.connect('C:/Users/peter/CM-ML-Class/1/data/database.sqlite')
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
	df = get_df_joined()
	print df.describe()