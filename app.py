from flask import Flask, render_template, request
#from crawler import Spider, save_function
from search import search_term

app = Flask(__name__) # defining a flask application

@app.route("/") 
def index_get():
    return render_template("index.html") # return the rendered html file

# @app.route("/crawl") 
# def crawler_rss(): 
#     print('Starting crawling')
#     url = 'https://www.hubermanlab.com/podcast'
#     crawler = Spider(url)
#     crawler.run()
#     save_function(crawler.content)
#     print('Finished crawling')
#     print('Starting indexing')
#     index(schema)
#     print('Finished indexing')
#     return render_template("index.html") # return the rendered html file

@app.route("/search", methods=["POST"]) 
def search():
    query = request.form["search_query"] 
    results = search_term(query)
    return render_template("results.html", result=results, word=query) # return the rendered html

#main function
if __name__ == "__main__":
    app.run(debug=True)