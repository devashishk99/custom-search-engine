from whoosh.index import create_in, open_dir
from whoosh import qparser
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.query import *

def search_term(term):
	ix = open_dir("index")
	res = []
	with ix.searcher() as searcher:
		og = qparser.OrGroup.factory(0.9)
		query = MultifieldParser(["title", "topic"], ix.schema).parse(term)
		results = searcher.search(query)
		for r in results:
			res.append({
                'title': r.highlights('title'),
                'link': r['link'],
                'topic': r['topic'],
                'description': r['body']
                })
	return res
		