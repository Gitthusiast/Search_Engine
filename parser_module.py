from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from document import Document


class Parse:

    def __init__(self):
        self.stop_words = stopwords.words('english')

    def parse_sentence(self, text):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """

        text = "1000 in 6 % and 7.9% 4567983 so 123.5 thousand and 100,000 = 1,123% 8000382195 and 3.3 percent is 60 percentage so 4.04 Billion"
        text_tokens = word_tokenize(text)
        parsed_list = []

        for index, token in enumerate(text_tokens):

            if token not in self.stop_words:

                formatted_token = None

                # parse numeric values
                if self.is_float(token):
                    numeric_token = float(token.replace(",", ""))

                    # format large numbers
                    if 1000 <= numeric_token < 1000000:
                        formatted_token = "{num:.3f}".format(num=(numeric_token / 1000)).rstrip("0").rstrip(".") + "K"
                    elif text_tokens[index + 1].lower() == "thousand":
                        formatted_token = str(numeric_token).rstrip("0").rstrip(".") + "K"
                    elif 1000000 <= numeric_token < 1000000000:
                        formatted_token = "{num:.3f}".format(num=numeric_token / 1000000).rstrip("0").rstrip(".") + "M"
                    elif text_tokens[index + 1].lower() == "million":
                        formatted_token = str(numeric_token).rstrip("0").rstrip(".") + "M"
                    elif 1000000000 <= numeric_token:
                        formatted_token = "{num:.3f}".format(num=numeric_token / 1000000000).rstrip("0").rstrip(".") + "B"
                    elif text_tokens[index + 1].lower() == "billion":
                        formatted_token = str(numeric_token).rstrip("0").rstrip(".") + "B"
                    else:  # Not a large number
                        formatted_token = numeric_token

                    # parse percentage
                    lower_case_next_token = text_tokens[index + 1].lower()
                    if lower_case_next_token == "%" or lower_case_next_token == "percent" \
                            or lower_case_next_token == "percentage":
                        formatted_token = str(formatted_token).rstrip("0").rstrip(".") + "%"

                # parse entities
                # entity is every sequence of tokens starting with a capital letter \
                # and appearing at least twice in the entire corpus
                if token[0].isupper():

                    current_token = token
                    entities = set()
                    while current_token[0].isupper():
                        if current_token not in entities:
                            entities.add(current_token)

                            if "-" in token:
                                splitted_by_dash = token.split("-")
                                insert_index = index + 1
                                for splitted_token in splitted_by_dash:
                                    text_tokens.insert(insert_index, splitted_token)
                                    insert_index = insert_index + 1

                if formatted_token is not None:
                    parsed_list.append(formatted_token)

        print(parsed_list)
        return parsed_list

    def parse_doc(self, doc_as_list):
        """
        This function takes a tweet document as list and break it into different fields
        :param doc_as_list: list re-presenting the tweet.
        :return: Document object with corresponding fields.
        """
        tweet_id = doc_as_list[0]
        tweet_date = doc_as_list[1]
        full_text = doc_as_list[2]
        url = doc_as_list[3]
        retweet_text = doc_as_list[4]
        retweet_url = doc_as_list[5]
        quote_text = doc_as_list[6]
        quote_url = doc_as_list[7]
        term_dict = {}
        tokenized_text = self.parse_sentence(full_text)

        doc_length = len(tokenized_text)  # after text operations.

        for term in tokenized_text:
            if term not in term_dict.keys():
                term_dict[term] = 1
            else:
                term_dict[term] += 1

        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict, doc_length)
        return document

    """
    Verify if a string can be converted to float
    :param number - string to be converted
    :return Boolean - can be converted or not
    """
    def is_float(self, number):

        try:
            float(number)
            if number != "infinity":
                return True
        except ValueError:

            if number.replace(",", "").isnumeric():
                return True
            return False
