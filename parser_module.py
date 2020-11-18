from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from document import Document


class Parse:

    def __init__(self):
        self.stop_words = stopwords.words('english')

    def parse_hashtag2(self, text_tokens, i):
        """
        This function parses the hashtag including tokens, according to the rules.
        :param text_tokens: tokens from the text
        :return:
        """
        if len(text_tokens) > i + 1:
            hashtag = text_tokens[i + 1]
            text_tokens.remove(text_tokens[i + 1])
            from_index = 0  # indicating where to slice the string from
            joined_hashtag = ""
            insertion_index = 0  # indication where to insert the new token
            j = 0  # iterator for the hashtag string
            while j < len(hashtag):
                if hashtag[j].isupper() or j == len(hashtag) - 1 or hashtag[j] in ['.', '…', ',', '_', '-', '.']:
                    if j == len(hashtag) - 1:
                        if hashtag[j] not in ['.', '…', ',', '_', '-', '.']:
                            text_tokens.insert(i + 1 + insertion_index, hashtag[from_index:j + 1].lower())
                            joined_hashtag += hashtag[from_index + 1:j + 1].lower()
                            insertion_index += 1
                    elif hashtag[j].isupper():
                        if len(hashtag) > j+1 and hashtag[j+1].isupper():  # interpret word as acronym
                            if hashtag[from_index:j] != '':
                                text_tokens.insert(i + 1 + insertion_index, hashtag[from_index:j].lower())
                                from_index = j
                                insertion_index += 1
                            while j < len(hashtag):
                                if len(hashtag) > j + 1 and not hashtag[j+1].isupper():
                                    if from_index == 0:
                                        text_tokens.insert(i + 1 + insertion_index, hashtag[from_index:j + 1].lower())
                                        joined_hashtag += hashtag[from_index:j + 1].lower()
                                    else:
                                        text_tokens.insert(i + 1 + insertion_index, hashtag[from_index + 1:j + 1].lower())
                                        joined_hashtag += hashtag[from_index + 1:j + 1].lower()
                                    from_index = j + 1
                                    insertion_index += 1
                                    break
                                j += 1
                            if j == len(hashtag):
                                text_tokens.insert(i + 1 + insertion_index, hashtag[from_index:j].lower())
                                joined_hashtag += hashtag[from_index:j].lower()
                                insertion_index += 1
                                break
                        elif j != 0:
                            text_tokens.insert(i + 1 + insertion_index, hashtag[from_index:j].lower())
                            from_index = j
                            insertion_index += 1
                    elif hashtag[j] in ['.', '…', ',', '_', '-', '.']:
                        if hashtag[from_index:j] != '':
                            text_tokens.insert(i + 1 + insertion_index, hashtag[from_index:j].lower())
                            from_index = j + 1
                            insertion_index += 1

                elif j < len(hashtag) and not hashtag[j] in ['.', '…', ',', '_', '-', '.', '']:
                    joined_hashtag += hashtag[j].lower()

                j += 1

            text_tokens[i] += joined_hashtag

    def parse_hashtag_underscore(self, text_tokens, i):
        token = text_tokens[i+1]
        text_tokens.remove(text_tokens[i+1])
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
        text_tokens.remove(text_tokens[i + 1])
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

    def parse_hashtag_capital(self, text_tokens, i):

        token = text_tokens[i + 1]
        text_tokens.remove(text_tokens[i + 1])
        j = 0
        joined_hashtag = '#'
        from_index = 0
        insertion_index = 0
        while j < len(token):
            if j + 1 < len(token) and token[j].isupper() and token[j+1].isupper():
                if token[from_index:j] != '':
                    text_tokens.insert(i + 1 + insertion_index, token[from_index:j].lower())
                    from_index = j
                    insertion_index += 1
                while j < len(token) and token[j].isupper():
                    j += 1
                text_tokens.insert(i + 1 + insertion_index, token[from_index:j])
                joined_hashtag += token[from_index:j].lower()
                from_index = j
                insertion_index += 1
                j -= 1
            elif token[j].isupper() and j != 0:
                if token[from_index:j] != '':
                    text_tokens.insert(i + 1 + insertion_index, token[from_index:j].lower())
                    from_index = j
                    insertion_index += 1
                joined_hashtag += token[j].lower()
            else:  # lower case letters
                joined_hashtag += token[j].lower()
            j += 1
        if token[from_index:len(token)] != '':
            text_tokens.insert(i + 1 + insertion_index, token[from_index:j].lower())
        text_tokens[i] = joined_hashtag

    def parse_hashtag(self, text_tokens, i):

        # parsing snake case
        if len(text_tokens) > i + 1 and text_tokens[i+1].count('_') > 0:
            self.parse_hashtag_underscore(text_tokens, i)

        # parsing pascal and camel cases
        camel_case = True
        if len(text_tokens) > i + 1:
            for j in range(len(text_tokens[i+1])-1):
                if text_tokens[i+1][j].isupper() and text_tokens[i+1][j+1].isupper():
                    camel_case = False  # not camel case - word of type "CULTforGOOD" different parsing
            if camel_case:
                self.parse_hashtag_camel_case(text_tokens, i)
            else:
                self.parse_hashtag_capital(text_tokens, i)  # parsing words with capital letters - acronyms

    def parse_tagging(self, text_tokens, i):

        if len(text_tokens) > i+1:
            text_tokens[i] += text_tokens[i+1]
            text_tokens.remove(text_tokens[i+1])

    def parse_url(self, text_tokens, i):
        if len(text_tokens) > i+1:
            # text_tokens.remove(text_tokens[i+1])  # removing ':'
            del text_tokens[i+1]  # removing ':'
            link_token = text_tokens[i+1]
            text_tokens.remove(text_tokens[i + 1])  # to remove the previous token
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


    def parse_sentence(self, text):

        # text = "6% 10.6 percent 11 percentage 7 % %7 11.1%"
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """
        text = "#stay_at_home #StayAtHome #stayAtHome"
        print(text)
        text_tokens = word_tokenize(text)

        for index, token in enumerate(text_tokens):
            if token == '#':
                self.parse_hashtag(text_tokens, index)
            if token == '@':
                self.parse_tagging(text_tokens, index)
            if token == 'https' or token == 'http':
                self.parse_url(text_tokens, index)

        """
        print(str(text_tokens.count(':')) + "\n")
        if text_tokens.count(':') != 0:
            print(text_tokens[text_tokens.index(':') - 1])
        """

        print(text_tokens)
        print("\n\n")



        text_tokens_without_stopwords = [w.lower() for w in text_tokens if w not in self.stop_words]
        return text_tokens_without_stopwords

    def parse_doc(self, doc_as_list):
        """
        This function takes a tweet document as list and break it into different fields
        :param doc_as_list: list re-preseting the tweet.
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
