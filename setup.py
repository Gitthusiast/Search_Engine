import nltk
import search_engine
import demoji

demoji.download_codes()
nltk.download('stopwords')
nltk.download('punkt')

search_engine.main()
