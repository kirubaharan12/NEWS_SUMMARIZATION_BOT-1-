from flask import Flask,render_template
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
from newspaper import Article
import io
import nltk
from googletrans import Translator
from PIL import Image
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.lex_rank import LexRankSummarizer
nltk.download('punkt')
from flask import  request
app = Flask(__name__)

#FUCTION FOR FETCHING THE TRENDING NEWS
def fetch_top_news():
    site = 'https://news.google.com/news/rss'
    op = urlopen(site)
    rd = op.read()
    op.close()
    sp_page = soup(rd, 'xml')
    news_list = sp_page.find_all('item')
    return news_list

#FUNCTION FOR FETCHING THE NEWS FOR TOPIC
def fetch_news_search_topic(topic):
    site = 'https://news.google.com/rss/search?q={}'.format(topic)
    op = urlopen(site)
    rd = op.read()
    op.close()
    sp_page = soup(rd, 'xml')
    news_list = sp_page.find_all('item')
    return news_list

#FUNCTION FOR FETCHING THE NEWS FOR SOME CATEGORY
def fetch_category_news(topic):
    site = 'https://news.google.com/news/rss/headlines/section/topic/{}'.format(topic)
    op = urlopen(site)
    rd = op.read()
    op.close()
    sp_page = soup(rd, 'xml')
    news_list = sp_page.find_all('item')
    return news_list



#FUCTION FOR RETURN THE NEWS DAT
def fetch_news_data(list_of_news,news_quantity):
   
    news_quantity = 5  # Example value

    news_list = []
    c=0

    for c, news in enumerate(list_of_news, start=1):
        if c > news_quantity:
            break

        news_data = Article(news.link.text)
        try:
            news_data.download()
            news_data.parse()
            news_data.nlp()
        except Exception as e:
            print("Error:", e)
            continue

        news_info = {
            'index': c,
            'title': news.title.text,
            'summary': news_data.summary,
            'source': news.source.text,
            'link': news.link.text,
            'published_date': news.pubDate.text,
          
        }
        news_list.append(news_info)

    return news_list

# Define the route for the home page
@app.route('/', methods=['GET', 'POST'])
def home():
    title = None
    summary = None
    language=None
    translator = Translator()
    if request.method == 'POST':
        url = request.form['url']
        language=request.form['language']
        title, summary = summarize_article_from_url(url)
        if language=='eng':
            return render_template('index.html', title=title, summary=summary)
        else:
            title = translator.translate(title, src='en', dest=language)
            title=title.text
            summary = translator.translate(summary, src='en', dest=language)
            summary=summary.text
    return render_template('index.html', title=title, summary=summary)

def summarize_article_from_url(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        article.nlp()
        original_title = article.title
        article_content = article.text
        parser = PlaintextParser.from_string(article_content, Tokenizer("english"))
        summarizer = LsaSummarizer()
        summary_sentences = summarizer(parser.document, 3)
        summary = " ".join([str(sentence) for sentence in summary_sentences])
        return original_title, summary
    except Exception as e:
        print("Error summarizing the article:", str(e))
        return None, None
    
@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'GET':
        news_list = fetch_top_news()
        news_list=fetch_news_data(news_list,5)
        return render_template('result.html',news_list=news_list, title="top news")
    elif request.method == 'POST':
        topic = request.form.get('topic')
        category = request.form.get('category')
        if topic:
            news_list = fetch_news_search_topic(topic)
            news_list=fetch_news_data(news_list,5)
            return render_template('result.html',news_list=news_list, title=topic)
        elif category:
            news_list = fetch_category_news(category)
            news_list=fetch_news_data(news_list,5)
            return render_template('result.html',news_list=news_list, title=category)
    return render_template('result.html',news_list=news_list)



if __name__ == '__main__':
    app.run(debug=True)

