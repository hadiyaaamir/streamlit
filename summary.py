# coding: utf-8 -*-

from summa.summarizer import summarize

from spacy.lang.ur.stop_words import STOP_WORDS 
from collections import Counter
from heapq import nlargest
import spacy

from bs4 import BeautifulSoup
import requests
import re

import streamlit as st



def summaryApp(): 
    #change for testing
    st.title('Summary App')

    tab1, tab2, tab3 = st.tabs(["Text Input", "Article Link", "Image"])

    with tab1:
        TextSummary()
    with tab2:
        LinkSummary()
    with tab3:
        ImageSummary()



def ext_summary_summa(text, ratio=0.5):
    summary = summarize(text, ratio=ratio, language="arabic")
    return summary


def ext_summary_2(text, ratio=0.5): 
    nlp = spacy.blank('ur')

    doc = nlp(text)
    tokens=[token.text for token in doc]

    punctuation="[:؛؟’‘٭ء،۔]+"

    word_frequencies={}
    for word in doc:
        if word.text.lower() not in STOP_WORDS:
            if word.text.lower() not in punctuation:
                if word.text not in word_frequencies.keys():
                    word_frequencies[word.text] = 1
                else:
                    word_frequencies[word.text] += 1

    max_frequency=max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word]=word_frequencies[word]/max_frequency

    sentences=[]
    sentence=[]
    punc="[:؛’‘٭ء،]+"
    puncc="؟۔"
    for word in text:
        if word not in punc:
            if word in puncc:
                sentence=text.split(word,1)
                sentences.append(sentence[0])
                text=sentence[1]

    sentence_tokens={}
    sentence_scores = {}
    for doc in nlp.pipe(sentences):
        sentence_tokens= (doc)
        # print (sentence_tokens)
        for word in sentence_tokens:
            if word.text.lower() in word_frequencies.keys():
                if sentence_tokens not in sentence_scores.keys():                            
                    sentence_scores[sentence_tokens]=word_frequencies[word.text.lower()]
                else:
                    sentence_scores[sentence_tokens]+=word_frequencies[word.text.lower()]

    select_length=int(len(sentence_scores)*ratio)

    summary=nlargest(select_length, sentence_scores,key=sentence_scores.get)

    s = ""
    for doc in summary:
        s = s + doc.text
    return s


# def abs_summary_summa(article_text):
#     WHITESPACE_HANDLER = lambda k: re.sub('\s+', ' ', re.sub('\n+', ' ', k.strip()))
#     model_name = "csebuetnlp/mT5_multilingual_XLSum"
#     tokenizer = AutoTokenizer.from_pretrained(model_name)
#     model = AutoModelForSeq2SeqLM.from_pretrained(model_name)


#     input_ids = tokenizer(
#         [WHITESPACE_HANDLER(article_text)],
#         return_tensors="pt",
#         truncation=True,
#         max_length=512
#     )["input_ids"]

#     output_ids = model.generate(
#         input_ids=input_ids,
#         max_length=84,
#         no_repeat_ngram_size=2,
#         num_beams=4
#     )[0]

#     summary = tokenizer.decode(
#         output_ids,
#         skip_special_tokens=True,
#         clean_up_tokenization_spaces=False
#     )

#     print(summary)
#     return summary
    
def getLinkArticle(url, news_website):

    page = requests.get(url,  headers= {'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(page.content, 'html.parser')

    #get article title
    title = soup.title.text
    #Only keep urdu text in title
    title = re.sub('(?<=[\u0600-\u06ff] )([A-Za-z -]+)', '' , title) #remove english text

    #get article
    article = ''

    if(news_website == 'Dawn News'):
        article = soup.select('.story__content p')
        for item in soup.find_all('strong'):
            item.decompose()
    
    elif(news_website == 'ARY News'):
        article = soup.select('.entry-content p')

    strArticle = ""
    for sentence in article:
        strArticle = strArticle + ' ' + sentence.text

    return title, strArticle



st.markdown(""" 
    <style> 
        .font {font-size:20px ; font-family: 'Urdu Typesetting'; text-align: right ; } 
        textarea {text-align: right; font-size:20px !important ; font-family: 'Urdu Typesetting' !important;}
    </style> """
    , unsafe_allow_html=True)


def TextSummary():

    form = st.form(key='my_form')
    text = form.text_area(label='Enter text to summarise')
    summary_type = form.selectbox('Type of Summary', ('Extractive 1', 'Extractive 2'))
    submit_button = form.form_submit_button(label='Submit')

    if submit_button and text != "":
        summarise(summary_type, text)        
    else:
        st.write('Enter text to summarise')


def LinkSummary():

    form = st.form(key='my_link_form')
    news_website = form.selectbox('News Website', ('Dawn News', 'ARY News'))
    link = form.text_input(label='Enter link to article')
    summary_type = form.selectbox('Type of Summary', ('Extractive 1', 'Extractive 2'))
    submit_button = form.form_submit_button(label='Submit')

    if submit_button and link != "":
        article = getLinkArticle(link, news_website)
        # st.markdown('<p class="font">'+ article[1] +'</p>', unsafe_allow_html=True)
        summarise(summary_type, article[1]) 
    else:
        st.write("Enter link to summarise")


def ImageSummary():
    form = st.form(key='my_image_form')
    uploaded_file = form.file_uploader("Attatch an Image")
    summary_type = form.selectbox('Type of Summary', ('Extractive 1', 'Extractive 2'))
    submit_button = form.form_submit_button(label='Submit')

    #chappofy. Keep whichever
    
    if uploaded_file is not None and submit_button:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()
        st.write(bytes_data)
    
        # To convert to a string based IO:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        st.write(stringio)

        # To read file as string:
        string_data = stringio.read()
        st.write(string_data)

        # Can be used wherever a "file-like" object is accepted:
        dataframe = pd.read_csv(uploaded_file)
        st.write(dataframe)

        #call function, summarise(), etc.

    else:
        st.write("Attatch image to summarise")


def summarise(summary_type, text): 
    if summary_type == 'Extractive 1':
        exSummary(text)
    elif summary_type == 'Extractive 2':
        exSummary2(text)


def exSummary(text):

    st.subheader('Summa Extractive Summariser')

    st.write('short')
    st.markdown('<p class="font">'+ ext_summary_summa(text, 0.1) +'</p>', unsafe_allow_html=True)

    st.write('regular')
    st.markdown('<p class="font">'+ ext_summary_summa(text, 0.25) +'</p>', unsafe_allow_html=True)

    st.write('long')
    st.markdown('<p class="font">'+ ext_summary_summa(text, 0.5) +'</p>', unsafe_allow_html=True)

    st.write('very long')
    st.markdown('<p class="font">'+ ext_summary_summa(text, 0.75) +'</p>', unsafe_allow_html=True)


def exSummary2(text): 

    st.subheader('Our Own Extractive Summariser')

    st.write('short')
    st.markdown('<p class="font">'+ ext_summary_2(text, 0.1) +'</p>', unsafe_allow_html=True)

    st.write('regular')
    st.markdown('<p class="font">'+ ext_summary_2(text, 0.2) +'</p>', unsafe_allow_html=True)

    st.write('long')
    st.markdown('<p class="font">'+ ext_summary_2(text, 0.3) +'</p>', unsafe_allow_html=True)

    st.write('very long')
    st.markdown('<p class="font">'+ ext_summary_2(text, 0.5) +'</p>', unsafe_allow_html=True)


summaryApp()

        

