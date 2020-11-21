from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from document import Document
from string import punctuation


class Parse:

    months = {"jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3, "apr": 4, "april": 4,
              "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7, "aug": 8, "august": 8, "sep": 9, "september": 9,
              "oct": 10, "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12}

    days = {"first": 1, "1st": 1, "second": 2, "2nd": 2, "third": 3, "fourth": 4, "4th": 4, "fifth": 5, "5th": 5,
            "sixth": 6, "6th": 6, "seventh": 7, "7th": 7, "eighth": 8, "8th": 8, "ninth": 9, "9th": 9,
            "tenth	": 10, "10th": 10, "eleventh": 11, "11th": 11, "twelfth": 12, "12th": 12, "thirteenth": 13,
            "13th": 13, "fourteenth": 14, "14th": 14, "fifteenth": 15, "15th": 15, "sixteenth": 16, "16th": 16,
            "seventeenth": 17, "17th": 17, "eighteenth": 18, "18th": 18, "nineteenth": 19, "19th": 19,
            "twentieth": 20, "twenty": 20, "thirtieth": 30, "30th": 30, "thirty": 30}

    def __init__(self):
        self.stop_words = stopwords.words('english')

    def parse_hashtag_underscore(self, text_tokens, i):
        token = text_tokens[i + 1]
        del text_tokens[i + 1]
        joined_hashtag = '#'
        from_index = 0
        insertion_index = 0
        for j in range(len(token)):
            if token[j] in ['.', '…', ',', '_', '-', '.']:
                joined_hashtag += token[from_index: j].lower()
                text_tokens.insert(i + 1 + insertion_index, token[from_index:j].lower())
                from_index = j + 1
                insertion_index += 1
        if token[from_index:len(token)] != '':
            joined_hashtag += token[from_index:len(token)].lower()
            text_tokens.insert(i + 1 + insertion_index, token[from_index:len(token)].lower())
        text_tokens[i] = joined_hashtag

    def parse_hashtag_camel_case(self, text_tokens, i):
        token = text_tokens[i + 1]
        del text_tokens[i + 1]
        j = 0
        joined_hashtag = '#'
        from_index = 0
        insertion_index = 0
        while j < len(token):
            if token[j].isupper() and j != 0:
                text_tokens.insert(i + 1 + insertion_index, token[from_index:j].lower())
                joined_hashtag += token[from_index:j].lower()
                from_index = j
                insertion_index += 1
            j += 1
        if token[from_index:len(token)] != '':
            joined_hashtag += token[from_index:len(token)].lower()
            text_tokens.insert(i + 1 + insertion_index, token[from_index:len(token)].lower())
        text_tokens[i] = joined_hashtag

    def parse_hashtag(self, text_tokens, i):

        # parsing snake case
        if len(text_tokens) > i + 1 and text_tokens[i+1].count('_') > 0:
            self.parse_hashtag_underscore(text_tokens, i)

        # parsing pascal and camel cases
        if len(text_tokens) > i + 1:
            self.parse_hashtag_camel_case(text_tokens, i)

    def parse_tagging(self, text_tokens, i):

        if len(text_tokens) > i + 1:
            text_tokens[i] += text_tokens[i + 1]
            del text_tokens[i + 1]

    def parse_url(self, text_tokens, i):
        if len(text_tokens) > i+1:
            del text_tokens[i+1]  # removing ':'
            link_token = text_tokens[i+1]
            del text_tokens[i + 1]  # to remove the previous token
            from_index = 0
            insertion_index = 0
            for j in range(len(link_token)):
                if link_token[j] == '/' or j == len(link_token) - 1:
                    if j == len(link_token) - 1:
                        text_tokens.insert(i + 1 + insertion_index, link_token[from_index:j + 1])
                        insertion_index += 1
                    elif link_token[from_index:j] != '':
                        text_tokens.insert(i + 1 + insertion_index, link_token[from_index:j])
                        insertion_index += 1
                    from_index = j + 1

    def parse_numeric_values(self, text_tokens, index):

        token = text_tokens[index]
        numeric_token = float(token.replace(",", ""))

        # format large numbers
        if 1000 <= numeric_token < 1000000:
            formatted_token = "{num:.3f}".format(num=(numeric_token / 1000)).rstrip("0").rstrip(".") + "K"
            text_tokens[index] = formatted_token
        elif len(text_tokens) > index + 1 and text_tokens[index + 1].lower() == "thousand":
            formatted_token = str(numeric_token).rstrip("0").rstrip(".") + "K"
            text_tokens[index] = formatted_token
            del text_tokens[index+1]
        elif 1000000 <= numeric_token < 1000000000:
            formatted_token = "{num:.3f}".format(num=numeric_token / 1000000).rstrip("0").rstrip(".") + "M"
            text_tokens[index] = formatted_token
        elif len(text_tokens) > index + 1 and text_tokens[index + 1].lower() == "million":
            formatted_token = str(numeric_token).rstrip("0").rstrip(".") + "M"
            text_tokens[index] = formatted_token
            del text_tokens[index+1]
        elif 1000000000 <= numeric_token:
            formatted_token = "{num:.3f}".format(num=numeric_token / 1000000000).rstrip("0").rstrip(".") + "B"
            text_tokens[index] = formatted_token
        elif len(text_tokens) > index + 1 and text_tokens[index + 1].lower() == "billion":
            formatted_token = str(numeric_token).rstrip("0").rstrip(".") + "B"
            text_tokens[index] = formatted_token
            del text_tokens[index+1]

        # parse percentage
        if len(text_tokens) > index + 1:
            lower_case_next_token = text_tokens[index + 1].lower()
            if lower_case_next_token == "%" or lower_case_next_token == "percent" \
                    or lower_case_next_token == "percentage":
                formatted_token = str(numeric_token).rstrip("0").rstrip(".") + "%"
                text_tokens[index] = formatted_token
                del text_tokens[index+1]

    def parse_date(self, text_tokens, index):

        if len(text_tokens) > index + 1:
            if len(text_tokens[index + 1]) > 2 and text_tokens[index + 1][-2:] == "th":
                i = 0

    def parse_sentence(self, text):

        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """
        # print(text)
        text_tokens = word_tokenize(text)

        index = 0
        while index < len(text_tokens):

            token = text_tokens[index]
            if token not in self.stop_words and token not in ["RT"] and token not in \
                    punctuation.replace('#', '').replace('@', '').replace('%', '').replace('$', '') and token.isascii():

                if token == '#':
                    self.parse_hashtag(text_tokens, index)
                if token == '@':
                    self.parse_tagging(text_tokens, index)
                if token == 'https' or token == 'http':
                    self.parse_url(text_tokens, index)

                # parse numeric values
                if self.is_float(token):
                    self.parse_numeric_values(text_tokens, index)

                if token.lower() in self.months:
                    self.parse_date(text_tokens, index)

                # parse entities
                # entity is every sequence of tokens starting with a capital letter \
                # and appearing at least twice in the entire corpus
                # if token[0].isupper():
                #
                #     current_token = token
                #     entities = set()
                #     while current_token[0].isupper():
                #         if current_token not in entities:
                #             entities.add(current_token)
                #
                #             if "-" in token:
                #                 splitted_by_dash = token.split("-")
                #                 insert_index = index + 1
                #                 for splitted_token in splitted_by_dash:
                #                     text_tokens.insert(insert_index, splitted_token)
                #                     insert_index = insert_index + 1
                index += 1
            else:
                if not token.isascii():
                    i = 0
                    valid_token = ""
                    while i < len(token):
                        if token[i].isascii():
                            valid_token += token[i]
                        i += 1
                    if valid_token != '':
                        text_tokens[index] = valid_token
                    else:
                        del text_tokens[index]
                else:
                    del text_tokens[index]

        print(text_tokens)

        return text_tokens

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
            float(number.replace(",", ""))
            if number.lower() != "infinity":
                return True
        except ValueError:
            return False
