import os, ast
from whoosh.index import create_in, open_dir

def index(schema):
    content = []
    with open('podcasts.txt', 'r') as content_file:
        content = ast.literal_eval(content_file.read())
            
    # creating the index
    if not os.path.exists("index"):
        os.mkdir("index")
        
    ix = create_in("index", schema)
    ix = open_dir("index")
    writer = ix.writer()

    # add document details into index
    for p in content:
        writer.add_document(title=p['title'],
                            topic=p['topic'],
                            link=p['link'],
                            body=p['description'])
        
    writer.commit()
		
    
	