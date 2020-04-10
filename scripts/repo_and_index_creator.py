import json
import spacy
from collections import defaultdict
from nltk import word_tokenize 


def get_compound_named_entities(text):
    elems = []
    doc = nlp(text)
    for ent in doc.ents:
        if len(word_tokenize(ent.text)) >= 2:
            elems.append(ent.text)
    return elems

def get_tokens(text):
    tokens = word_tokenize(text) + get_compound_named_entities(text)
    return tokens

def create_repo(corpus):
    return {docid: get_tokens(text) for docid, text in corpus.items()}

def create_index(repo):
    indexed = defaultdict(set)
    for doc_id, words in repo.items():
        for word in words:
            indexed[word].add(doc_id)

    return {word: list(doc_ids) for word, doc_ids in indexed.items()}

def main():
    with open("./corpus.json", 'r') as file:
        corpus = json.load(file)
    repo = create_repo(corpus)
    with open("repository.json", 'w') as file_repo:
        json.dump(repo, file_repo, indent=4)
    index = create_index(repo)
    with open("index.json", 'w') as file_repo:
        json.dump(index, file_repo, indent=4)


if __name__ == '__main__':
    nlp = spacy.load("en_core_web_sm")
    main()
