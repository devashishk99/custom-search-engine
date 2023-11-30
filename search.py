from whoosh.index import create_in, open_dir
from whoosh import qparser
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.query import *
from whoosh.searching import *

def search_term(term):
    ix = open_dir("index")
    res = []
    dym_flag = 0
    q = ''
    with ix.searcher() as searcher:
        og = qparser.OrGroup.factory(0.9)
        query = QueryParser("title", ix.schema, group=og).parse(term)
        #corrector = searcher.corrector("title")
        corrected = searcher.correct_query(query, term)
        if corrected.query != query:
            print("Did you mean:", corrected.string)
            dym_flag = 1
            q = corrected.string
            query = QueryParser("title", ix.schema, group=og).parse(q)
        results = searcher.search(query) 
        for r in results:
            res.append({
                'title': r.highlights('title'),
                'link': r['link'],
                'topic': r['topic'],
                'description': r['body']
                })
        print(dym_flag)

    return res, dym_flag, q      