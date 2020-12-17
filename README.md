# Search_Engine
In order for you to be able to run the search engine these are the requierments:
click==7.1.2
joblib==0.17.0
nltk==3.5
numpy==1.15.4
pandas==1.1.4
pyarrow==2.0.0
python-dateutil==2.8.1
pytz
regex==2020.10.28
six==1.15.0
tqdm==4.51.0
demoji==0.3.0
pyspellchecker==0.5.5

Before running the engine please run setup.py. This will download the needed packages for nltk and demoji. 
Please specify for search_engine.main() the following paramaters:
corpus_path - the path to where your data (corpus) is located.
output_path - the path to where the posting files and inverted_index dictionary will be saved
stemming - boolean indicating if you would like to stemm the terms
queries - a list of query strings or a path to a file of queries seperated by new lines
num_doc_to_retrieve - number of top relevant documents to retrieve for the query