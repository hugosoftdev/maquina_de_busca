import spacy
import json
from Levenshtein import distance as levenshtein_distance
from nltk.tokenize import word_tokenize


def get_adverbs_and_adjectives(query):
    doc = nlp(query)
    elems = []
    for token in doc:
        if token.pos_ in ("ADV", "ADJ"):
            elems.append(token.text)
    return elems

def get_query_support_elements(query, mainElements):
    elems = []
    temp  = get_adverbs_and_adjectives(query)
    for i in temp:
        if i not in mainElements:
            elems.append((i,1))
    temp  = get_nouns_and_verbs(query)
    for i in temp:
        if i not in mainElements:
            elems.append((i,2))
    return list(set(elems))

def tokenize_sentence(query):
    return word_tokenize(query)

def get_nouns_and_verbs(query):
    doc = nlp(query)
    elems = []
    for token in doc:
        if token.pos_ in ("AUX", "VERB", "PROPN", "NOUN"):
            elems.append(token.text)
    return elems

def get_named_entities(query):
    elems = []
    doc = nlp(query)
    for ent in doc.ents:
        elems.append(ent.text)
    return elems

def get_query_elements(query):
    elems = get_named_entities(query)
    if len(elems) > 0:
        return elems
    elems = get_nouns_and_verbs(query)
    if len(elems) > 0:
        return elems
    return tokenize_sentence(query)

def get_correspondent_word(elem,index):
    correspondence_ranking = []
    seen_distances = []
    max_acceptable_distance = 3
    for key in index:
        distance = levenshtein_distance(elem,key)
        if distance == 1:
            return key
        if distance <= max_acceptable_distance:
            if distance not in seen_distances:
                seen_distances.append(distance)
                correspondence_ranking.append((key,distance))          
    correspondence_ranking.sort(key=lambda x: x[1], reverse=False)
    if len(correspondence_ranking) == 0:
        return None
    return correspondence_ranking[0][0]

def correct_query(query, query_elements, index):
    corrections = {}
    for elem in query_elements:
        if elem not in index:
            correction = get_correspondent_word(elem, index)
            if correction != None:
                corrections[elem] = correction
    corrected_query =  query
    for key in corrections:
        corrected_query = corrected_query.replace(key, corrections[key])
    return corrected_query, corrections

def rank_documents(doc_ids, repo, main_elements, differential_elements):
    doc_id_points = {doc_id: 0 for  doc_id in doc_ids}
    for main_el in main_elements:
        for doc_id in doc_ids:
            doc_id_points[doc_id] += repo[doc_id].count(main_el) * 3

    for dif_el in differential_elements:
        for doc_id in doc_ids:
            doc_id_points[doc_id] += repo[doc_id].count(dif_el[0]) * dif_el[1]

    docs_ids_sorted = list(doc_id_points.items())
    docs_ids_sorted.sort(key=lambda x: x[1], reverse=True)
    return [ x[0] for x in  docs_ids_sorted]



def get_results(query, main_elements, differential_elements, n, repo,index,corpus):
    results_ids = set()
    if set(main_elements) <= set(index.keys()):
        for ele in main_elements:
            for doc_id in index[ele]:
                results_ids.add(doc_id)
    ranked_doc_ids = rank_documents(list(results_ids), repo, main_elements, differential_elements)
    if len(ranked_doc_ids) > n:
        ranked_doc_ids = ranked_doc_ids[:n]
    return [corpus[doc_id] for doc_id in ranked_doc_ids]
    

def main(repo,index,corpus):
    query = ""
    while not query: 
        query = str(input("Type your query: ")).strip()

    query_response = {"query": query}
    query_response['must_have'] = get_query_elements(query)

    correction, dict_corrections = correct_query(query, query_response['must_have'], index)
    if correction != query:
        intention = ""
        while intention not in ("Y","N"):
            intention = str(input(f"Did you meant: `{correction}`? (Y/N): ")).upper()
        if intention == 'Y':
            query_response['must_have'] = [dict_corrections[x] if x in dict_corrections else x for x in query_response['must_have'] ]
            query_response['query_corrected_to'] = correction
            query = correction


    if len(word_tokenize(query)) == len(query_response['must_have']):
        query_response['nice_to_have'] = []
    else:
        query_response['nice_to_have'] = get_query_support_elements(query, query_response['must_have'])

    number_of_results = 3
    print("Searching...")
    results = get_results(query, query_response['must_have'],query_response['nice_to_have'], number_of_results, repo,index,corpus)



    print("Original query: ", query_response['query'])

    if 'query_corrected_to' in query_response:
        print("Query corrected to: ", query_response['query_corrected_to'])

    print("Main elements found in the query: ", query_response['must_have'])

    if len(query_response['nice_to_have']) > 0:
        print("Intersting elements found in the query: ", query_response['nice_to_have'])
    
    if len(results) == 0:
        print("\n Sorry, couldn't find any relevant document for this query. \n")
    else:
        print(f"\n\n{len(results)} results was found: \n\n")
        for result in results:
            print(f"{result}\n\n\n")


if __name__ == '__main__':
    print("Loading...")
    nlp = spacy.load("en_core_web_sm")
    with open("./repository.json", 'r') as file:
        repo = json.load(file)
    with open("./index.json", 'r') as file:
        index = json.load(file)
    with open("./corpus.json", 'r') as file:
        corpus = json.load(file)
    main(repo,index,corpus)
