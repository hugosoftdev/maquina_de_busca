import json
from nltk.corpus import reuters

def main():

    docs = {}
    for fileid in reuters.fileids():
        docs[fileid] = reuters.raw(fileid)

    with open("corpus.json", 'w') as file:
        json.dump(docs, file, indent=4)


if __name__ == '__main__':
    main()
