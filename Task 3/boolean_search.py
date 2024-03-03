import re
import pymorphy2
from os import path


class SearchQuery:
    def __init__(self, query: str, files: set):
        self.query = query
        self.files = files

    def __and__(self, other):
        return SearchQuery(self.query + ' & ' + other.query, self.files & other.files)

    def __or__(self, other):
        return SearchQuery(self.query + ' | ' + other.query, self.files | other.files)

    def __sub__(self, other):
        return SearchQuery(self.query + ' ! ' + other.query, self.files - other.files)


class BooleanSearch:
    def __init__(self):
        self.inverted_index_file_name = path.dirname(__file__) + '/inverted_index.txt'
        self.morph = pymorphy2.MorphAnalyzer()
        self.index = dict()
        self.read_inverted_index()

    def read_inverted_index(self):
        file = open(self.inverted_index_file_name, 'r')
        lines = file.readlines()
        for line in lines:
            items = re.split('\\s+', line)
            token = items[0]
            files = set()
            for i in range(2, len(items) - 1):
                files.add(int(items[i]))
            self.index[token] = SearchQuery(token, files)
        file.close()

    def search(self, search_words):
        tokens = re.split('\\s+', search_words)
        parsed_token = self.morph.parse(tokens[0])[0]
        start_token = parsed_token.normal_form if parsed_token.normalized.is_known else tokens[0].lower()
        result = SearchQuery('', set())
        if start_token in self.index.keys():
            result = self.index[start_token]
        i = 1
        while i < len(tokens):
            if tokens[i] == '&' and i + 1 < len(tokens):
                parsed_token = self.morph.parse(tokens[i + 1])[0]
                current_token = parsed_token.normal_form if parsed_token.normalized.is_known else tokens[i + 1].lower()
                if current_token in self.index.keys():
                    new_result = self.index[current_token]
                    result = result & new_result
                i += 1
            elif tokens[i] == '!' and i + 1 < len(tokens):
                parsed_token = self.morph.parse(tokens[i + 1])[0]
                current_token = parsed_token.normal_form if parsed_token.normalized.is_known else tokens[i + 1].lower()
                if current_token in self.index.keys():
                    new_result = self.index[current_token]
                    result = result - new_result
                i += 1
            elif tokens[i] == '|' and i + 1 < len(tokens):
                parsed_token = self.morph.parse(tokens[i + 1])[0]
                current_token = parsed_token.normal_form if parsed_token.normalized.is_known else tokens[i + 1].lower()
                if current_token in self.index.keys():
                    new_result = self.index[current_token]
                    result = result | new_result
                i += 1
            else:
                parsed_token = self.morph.parse(tokens[i])[0]
                current_token = parsed_token.normal_form if parsed_token.normalized.is_known else tokens[i].lower()
                if current_token in self.index.keys():
                    new_result = self.index[current_token]
                    result = result | new_result
            i += 1
        result = list(result.files)
        result.sort()
        return result


if __name__ == '__main__':
    boolean_search = BooleanSearch()
    print('омский')
    print(boolean_search.search('омский'))
    print('депутат')
    print(boolean_search.search('депутат'))
    print('омские & депутатов')
    print(boolean_search.search('омские & депутатов'))
    print('омскую | депутаты')
    print(boolean_search.search('омскую | депутаты'))
    print('омских ! депутату')
    print(boolean_search.search('омских ! депутату'))
    print('омского депутата')
    print(boolean_search.search('омского депутата'))
    print('намекать')
    print(boolean_search.search('намекать'))
    print('омский & депутат | намекает')
    print(boolean_search.search('омский & депутат | намекает'))
