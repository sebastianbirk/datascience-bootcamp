import pandas as pd

def azureml_main(dataframe1 = None):
	dataframe1['Dollar/Horsepower'] = dataframe1.price / dataframe1.horsepower
	return dataframe1