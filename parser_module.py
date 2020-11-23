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
        if len(text_tokens) > i + 1 and text_tokens[i + 1].count('_') > 0:
            self.parse_hashtag_underscore(text_tokens, i)

        # parsing pascal and camel cases
        if len(text_tokens) > i + 1:
            self.parse_hashtag_camel_case(text_tokens, i)

    def parse_tagging(self, text_tokens, i):

        if len(text_tokens) > i + 1:
            text_tokens[i] += text_tokens[i + 1]
            del text_tokens[i + 1]

    def parse_url(self, text_tokens, i):
        if len(text_tokens) > i + 1:
            del text_tokens[i + 1]  # removing ':'
            link_token = text_tokens[i + 1]
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

    def is_float(self, number):

        """
        Verify if a string can be converted to float
        :param number - string to be converted
        :return Boolean - can be converted or not
        """

        try:
            float(number.replace(",", ""))
            if number.lower() != "infinity":
                return True
        except ValueError:
            return False

    def parse_numeric_values(self, text_tokens, index):

        """
        Parse numeric tokens according to specified rules.
        Any number in the thousands, millions and billions will be abbreviated to #K, #M and #B respectively
        Any number signifying percentage will be shown as #%
        Fractions of the format #/# will stay the same
        :param text_tokens: list of tokens to be parsed
        :param index: index of currently parsed token
        """

        token = text_tokens[index]
        numeric_token = float(token.replace(",", ""))

        # format large numbers
        # any number in the thousands, millions and billions will be abbreviated to #K, #M and #B respectively
        if 1000 <= numeric_token < 1000000:
            formatted_token = "{num:.3f}".format(num=(numeric_token / 1000)).rstrip("0").rstrip(".") + "K"
            text_tokens[index] = formatted_token
        elif len(text_tokens) > index + 1 and text_tokens[index + 1].lower() == "thousand":
            formatted_token = str(numeric_token).rstrip("0").rstrip(".") + "K"
            text_tokens[index] = formatted_token
            del text_tokens[index + 1]
        elif 1000000 <= numeric_token < 1000000000:
            formatted_token = "{num:.3f}".format(num=numeric_token / 1000000).rstrip("0").rstrip(".") + "M"
            text_tokens[index] = formatted_token
        elif len(text_tokens) > index + 1 and text_tokens[index + 1].lower() == "million":
            formatted_token = str(numeric_token).rstrip("0").rstrip(".") + "M"
            text_tokens[index] = formatted_token
            del text_tokens[index + 1]
        elif 1000000000 <= numeric_token:
            formatted_token = "{num:.3f}".format(num=numeric_token / 1000000000).rstrip("0").rstrip(".") + "B"
            text_tokens[index] = formatted_token
        elif len(text_tokens) > index + 1 and text_tokens[index + 1].lower() == "billion":
            formatted_token = str(numeric_token).rstrip("0").rstrip(".") + "B"
            text_tokens[index] = formatted_token
            del text_tokens[index + 1]

        # parse percentage
        # any number signifying percentage will be shown as #%
        if len(text_tokens) > index + 1:
            lower_case_next_token = text_tokens[index + 1].lower()
            if lower_case_next_token == "%" or lower_case_next_token == "percent" \
                    or lower_case_next_token == "percentage":
                formatted_token = str(numeric_token).rstrip("0").rstrip(".") + "%"
                text_tokens[index] = formatted_token
                del text_tokens[index + 1]

    def parse_date(self, text_tokens, index):

        if len(text_tokens) > index + 1:
            if len(text_tokens[index + 1]) > 2 and text_tokens[index + 1][-2:] == "th":
                i = 0

    def parse_entities(self, text_tokens, index, entities):

        """
        Identify possible entities in the document.
        A possible entity is any sequence of tokens starting with a capital letter
        :param text_tokens: list of tokens to be parsed
        :param index: index of current parsed token
        :param entities: dictionary of possible entities
        """
        current_token = text_tokens[index]
        entity = ""

        # find a sequence of terms with capital letters
        while index < len(text_tokens) - 1 and current_token[0].isupper():
            entity += current_token + " "
            index += 1
            current_token = text_tokens[index]
        entity.rstrip(" ")

        # add new possible entity to dictionary
        if entity not in entities:
            entities[entity] = 1
        else:
            entities[entity] += 1

    def parse_capital_letters(self, tokenized_text, term_dict):

        """
        Parses token according to capital letters rule.
        Ensures a uniform appearance of tokens - if a token only appears in capital form - record as upper case
        Else, record in lower case
        :param tokenized_text - list, list of parsed tokens
        :param term_dict - dictionary, record uniform token appearance according to rule in currently parsed document
        """

        index = 0
        while index < len(tokenized_text):

            token = tokenized_text[index]

            # save token as upper case
            # save token as lower and upper case
            formatted_token_lower = token.lower()
            formatted_token_upper = token.upper()

            # Add token to term dictionary
            # In the dictionary keep the term_frequency
            # term_frequency - how many times the term appeared in the document
            # key indicates if term is capital or lower case

            # Check if first letter is a capital letter
            if token[0].isupper():
                # check in which form the token appears in dictionary and update it accordingly
                if formatted_token_upper not in term_dict and formatted_token_lower not in term_dict:
                    term_dict[formatted_token_upper] = 1
                elif formatted_token_upper in term_dict:
                    term_dict[formatted_token_upper] += 1
                else:  # formatted_token_lower in capitals
                    term_dict[formatted_token_lower] += 1

            # If current term is lower case change key to lower case
            else:
                # check in which form the token appears in dictionary and update it accordingly
                if formatted_token_upper not in term_dict and formatted_token_lower not in term_dict:
                    term_dict[formatted_token_lower] = 1
                elif formatted_token_upper in term_dict:  # replace format of token from upper case to lower case
                    term_dict[formatted_token_lower] = term_dict[formatted_token_upper] + 1
                    term_dict.pop(formatted_token_upper, None)  # remove upper case form from the dictionary
                else:  # formatted_token_lower in capitals
                    term_dict[formatted_token_lower] += 1

            index += 1

    def parse_sentence(self, text, entities=None):

        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text: string - text to be parsed
        :param entities: dictionary - record possible entities in currently parsed document
        :return: list of parsed tokens
        """

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

                # parse dates
                if token.lower() in self.months:
                    self.parse_date(text_tokens, index)

                # parse entities
                # entity is every sequence of tokens starting with a capital letter \
                # and appearing at least twice in the entire corpus
                if index < len(text_tokens) - 1 and token[0].isupper() and text_tokens[index + 1][0].isupper():
                    self.parse_entities(text_tokens, index, entities)

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

        # dictionary for holding possible entities
        entities = dict()

        tokenized_text = self.parse_sentence(full_text, entities)

        doc_length = len(tokenized_text)  # after text operations.

        # parse token by lower or upper case rule
        # parsing will build the term dictionary in a uniform upper/lower form and calculate the term frequency
        self.parse_capital_letters(tokenized_text, term_dict)

        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict, doc_length, entities)
        return document
