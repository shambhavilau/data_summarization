import streamlit as st

from transformers import pipeline
from youtube_transcript_api import YouTubeTranscriptApi

from newspaper import Article 
import nltk

from bs4 import BeautifulSoup  # for web scraping, package for parsing html docs
import requests  # helps to send Http requests to wep pages


st.title("Data Summarisation")
st.write("Try out various data summarisation options")



@st.cache
def summarise_text(text):
    summarization = pipeline("summarization")
    summ_text = summarization(
        text, max_length=200, min_length=30, do_sample=False)  # [0]['summary_text']
    # do_sample tells to use Greedy decoder ie. return the word which has the highest probabliy of making sence.
    summ_text = summ_text[0]['summary_text']
    return(summ_text)

@st.cache(suppress_st_warning=True)
def summarise_video(v_url):
    video_id = v_url.split("=")[1]
    # produces JSON file with dictionaries
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    #transcript[0:20]
    temp = ""
    for i in transcript:
        temp += ' ' + i['text']  # fetches text from transcript
    summarization = pipeline("summarization")
    # default BERT model with pythorch

    no_iteration = int(len(temp)/1000)
    summarised_text = []
    for i in range(0, no_iteration+1):
        start = 0
        start = i * 1000
        end = (i+1) * 1000
        ans = summarization(temp[start:end])
        #ans = ans[0]
        ans = ans[0]['summary_text']
        summarised_text.append(ans)
    return (summarised_text)

@st.cache
def summarise_article(a_url):
    article = Article(a_url)
    # NLP code
    article.download()
    article.parse()
    nltk.download('punkt')
    article.nlp()

    author = article.authors
    pub_date = article.publish_date
    img = article.top_image
    #article_text = article.text
    article_summary = article.summary
    article_keywords = article.keywords
    return(author, pub_date, img, article_keywords, article_summary)

@st.cache
def summarise_longtext(b_url):
    summarization = pipeline("summarization")
    r = requests.get(b_url)
    # using beautiful soup
    soup = BeautifulSoup(r.text, 'html.parser')
    output_arr = soup.find_all(['h1', 'p'])  # produces array of separate lines
    output_text = [op.text for op in output_arr]  # looping through array
    ARTICLE = ' '.join(output_text)  # concatinating into single string
    # break sentences by  . ? !
    ARTICLE = ARTICLE.replace('.', '.<eos>')
    ARTICLE = ARTICLE.replace('!', '!<eos>')
    ARTICLE = ARTICLE.replace('?', '?<eos>')
    sentences = ARTICLE.split('<eos>')
    # break sentences in to lots
    max_lot = 500  # max words in a lot
    current_lot = 0
    lot = []  # a collection of sentence containing max of 500 words

    for s in sentences:
        if len(lot) == current_lot+1:
            if len(lot[current_lot]) + len(s.split(' ')) <= max_lot:
                lot[current_lot].extend(s.split(' '))
            else:
                current_lot += 1
                lot.append(s.split(' '))
        else:
            print(current_lot)
            lot.append(s.split(' '))
    # above code produes lots of words in each sentence.
    # now append the words in a string
    for lot_id in range(len(lot)):
        lot[lot_id] = ' '.join(lot[lot_id])
    # summarise text
    res = summarization(
        lot, max_length=120, min_length=30, do_sample=False)
    fin_res = ' '.join([summ['summary_text'] for summ in res])
    return(fin_res)


def get_option(option):
    if option == "Text Summarisation":
        sentence = st.text_area('Enter your text here...')
        is_summarized_button_clicked = st.button('Summarise')
        if is_summarized_button_clicked:
            st.write("Your Summary")
            result = summarise_text(sentence)
            st.write(result)
    elif option == "Video Summarisation":
        video_url = st.text_input('Enter youtube url here...')
        is_summarized_button_clicked = st.button('Summarise')
        if is_summarized_button_clicked:
            result = summarise_video(video_url)
            st.write(result)
    elif option == "Web Scrapping":
        article_url = st.text_input('Enter article url here...')
        is_summarized_button_clicked = st.button('Summarise')
        if is_summarized_button_clicked:
            result = summarise_article(article_url)
            st.write(result)
            summarise_article(article_url)
    else:
        blog_url = st.text_input('Enter blog url here...')
        is_summarized_button_clicked = st.button('Summarise')
        if is_summarized_button_clicked:
            result = summarise_longtext(blog_url)
            st.write(result)


option = st.sidebar.selectbox(
    "Select option",  ("Text Summarisation", "Web Scrapping", "Video Summarisation", "Long Text Summarisation"))

get_option(option)
