from whoosh.index import create_in, open_dir
from whoosh import qparser
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.query import *
from whoosh.searching import *

def add_html_tags(input_string, keyword, html_tag):
    """
    Add HTML tags around a specific keyword in a string.
    
    Parameters:
    - input_string: The input string to be processed.
    - keyword: The keyword to be surrounded by HTML tags.
    - html_tag: The HTML tag to be added around the keyword.
    
    Returns:
    - The modified string with HTML tags.
    """
    keyword_parts = keyword.split()
    for part in keyword_parts:
        pattern = re.compile(re.escape(part), re.IGNORECASE)
    
        # Search for the keyword in the input string
        match = pattern.search(input_string)

        # If the keyword is found, highlight it by adding html tags around it
        if match:
            found_keyword = match.group(0)
            input_string = pattern.sub(f'<{html_tag} class="match">{found_keyword}</{html_tag}>', input_string)

    return input_string


def search_term(term):
    """
    Searches for a specific keyword in the index.
    
    Parameters:
    - term: The input string to be searched.
    
    Returns:
    - The search results in the form of a dictionary.
    """
    ix = open_dir("index")
    res = []
    dym_flag = 0
    with ix.searcher() as searcher:
        og = qparser.OrGroup.factory(0.9)
        query = QueryParser("title", ix.schema, group=og).parse(term)
        #corrector = searcher.corrector("title")
        corrected = searcher.correct_query(query, term)
        if corrected.query != query:
            print("Did you mean:", corrected.string)
            dym_flag = 1
            term = corrected.string
            query = QueryParser("title", ix.schema, group=og).parse(term)
        results = searcher.search(query) 
        for r in results:
            res.append({
                'title': add_html_tags(r['title'], term, "b"),
                'link': r['link'],
                'topic': r['topic'],
                'description': r['body']
                })
        # print(dym_flag)
        # print(res)

    return res, dym_flag, term     