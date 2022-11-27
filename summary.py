# coding: utf-8 -*-

from summa.summarizer import summarize
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import re

from spacy.lang.ur.stop_words import STOP_WORDS 
from collections import Counter
from heapq import nlargest

import spacy

import streamlit as st

# st_text = '''کل میں نے آپ کو بتایا تھا کہ مجھے مکسڈ زون میں کچھ مزہ نہیں آیا اور میں جن کھلاڑیوں سے ملنا چاہتا تھا وہ نہیں ملے لیکن کل مکسڈ زون میں بہت اچھا تجربہ رہا۔
# کل نیدرلینڈز اور ایکواڈور کا میچ تھا جوکہ ایک ایک سے برابر رہا۔ اس کے بعد مکسڈ زون میں دونوں ٹیموں کے کھلاڑی رکے اور انہوں نے بہت لمبی باتیں کیں۔
# میں اس امید سے گیا تھا کہ نیدرلینڈ کی ٹیم میں انگریزی بولنے والے کافی کھلاڑی ہیں جن میں لیورپول کے کپتان ورجل وین ڈائک اور مینچسٹر سٹی کے نیتھن آرکے ہیں جوکہ کافی نامی گرامی کھلاڑی ہیں۔
# تو کل اچھا کام یہ ہوا کہ مکسڈ زون میں ورجل وین ڈائک میرے اشارے پر رک گئے۔ میں نے ان سے سوالات کیے اور انہوں نے بہت اچھے جوابات دیے۔
# میں جو اسٹوری کرنا چاہ رہا تھا اس کے لیے اگر آپ کو کھلاڑیوں کے جملے مل جائیں تو بہت خوشی ہوتی ہے۔ بعد ازاں میں نے نیتھن آرکے سے بھی سوالات کیے۔ اس وجہ سے کل مکسڈ زون کا تجربہ بہت اچھا تھا۔
# مکسڈ زون کے ساتھ ساتھ کل میچ کا تجربہ بھی اچھا رہا لیکن میچ کی بات کرنے سے پہلے یہ بات کرتے ہیں کہ ہم میچ میں پہنچے کیسے۔

# قطر نے یہاں صحافیوں کے لیے مین میڈیا سینٹر سے شٹل کا انتظام کیا ہے۔ مین میڈیا سینٹر میری رہائش سے 3 میٹرو اسٹاپ دُور ہے۔ اس سے پہلے یہ ہوتا تھا کہ مین میڈیا سینٹر سے آخری شٹل میچ سے ایک گھنٹہ قبل جاتی تھی۔ لیکن اب یہ وقت ڈیڑھ گھنٹہ ہوگیا تھا اور میں نے اس کا نوٹس نہیں دیکھا تھا۔
# میں معمول کے مطابق اٹھا اور چونکہ جمعے کا دن تھا تو ساڑے 11 بجے اپنی رہائش کے قریب ہی جمعے کی نماز پڑھی اور حساب یہی تھا کہ میں 12 بجے تک مین میڈیا سینٹر پہنچ جاؤں گا۔ میں جب میٹرو کے ذریعے مین میڈیا سینٹر پہنچا تو 12 بج چکے تھے اور میچ تھا ایک بجے۔ مین میڈیا سینٹر پہنچ کر معلوم ہوا کہ آخری شٹل تو جاچکی ہے۔
# '''



def summaryApp(): 

    st.title('Summary App')

    tab1, tab2, tab3 = st.tabs(["Text Input", "Article Link", "Image"])

    with tab1:
        TextSummary()


    # with tab2:



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




def TextSummary():

    st.markdown(""" 
    <style> 
        .font {font-size:20px ; font-family: 'Urdu Typesetting'; text-align: right ; } 
        textarea {text-align: right; font-size:20px !important ; font-family: 'Urdu Typesetting' !important;}
    </style> """
    , unsafe_allow_html=True)

    form = st.form(key='my_form')
    text = form.text_area(label='Enter text to summarise')
    
    summary_type = form.selectbox('Type of Summary', ('Extractive 1', 'Extractive 2', 'Abstractive'))

    submit_button = form.form_submit_button(label='Submit')

    st.subheader('Summa Summariser')

    if submit_button:
        if summary_type == 'Extractive 1':
            exSummary(text)
        elif summary_type == 'Extractive 2':
            exSummary2(text)
        
    else:
        st.write("Enter text to summarise")



def exSummary(text):
    st.write('short')
    st.markdown('<p class="font">'+ ext_summary_summa(text, 0.1) +'</p>', unsafe_allow_html=True)

    st.write('regular')
    st.markdown('<p class="font">'+ ext_summary_summa(text, 0.25) +'</p>', unsafe_allow_html=True)

    st.write('long')
    st.markdown('<p class="font">'+ ext_summary_summa(text, 0.5) +'</p>', unsafe_allow_html=True)

    st.write('very long')
    st.markdown('<p class="font">'+ ext_summary_summa(text, 0.75) +'</p>', unsafe_allow_html=True)


def exSummary2(text): 
    st.write('short')
    st.markdown('<p class="font">'+ ext_summary_2(text, 0.05) +'</p>', unsafe_allow_html=True)

    st.write('regular')
    st.markdown('<p class="font">'+ ext_summary_2(text, 0.2) +'</p>', unsafe_allow_html=True)

    st.write('long')
    st.markdown('<p class="font">'+ ext_summary_2(text, 0.3) +'</p>', unsafe_allow_html=True)

    st.write('very long')
    st.markdown('<p class="font">'+ ext_summary_2(text, 0.5) +'</p>', unsafe_allow_html=True)

    
print(ext_summary_2('''فیفا کے کچھ میچ ایسے ہوتے ہیں جو آپ اس لیے کور کرنا چاہتے ہیں کیونکہ وہ میچ بہت بڑے میچ ہوتے ہیں۔ ارجنٹینا اور میکسیکو کے مابین ہونے والا میچ بھی ان بڑے میچوں میں شمار ہونا تھا۔
لیکن یہاں ایک مسئلہ تھا۔ قطر میں جتنے بھی صحافی آئے ہوئے ہیں ان میں سے بہت ساروں نے اس میچ کو کور کرنے کی درخواست دی ہوئی تھی مگر فیفیا کے پاس ہر میچ کے لیے مخصوص میڈیا سیٹیں ہوتی ہیں اور جب صحافیوں کی درخواستیں ان سیٹوں سے زیادہ ہوجاتی ہیں تو باقی درخواستوں کو رد کردیا جاتا ہے۔
اس کے لیے فیفا کے ایک فارمولہ بنایا ہوا ہے اور وہ یہ ہے کہ جن 2 ٹیموں کا میچ ہونا ہے سب سے پہلے ان ممالک کے صحافیوں کو اجازت دی جاتی ہے۔ اس کے بعد ان دونوں کی کنفیڈریشن کے صحافیوں کو اجازت ملتی ہے۔ ارجنٹینا کے لیے ساؤتھ امریکین کنفیڈریشن جسے CONMEBOL کہتے ہیں وہ ہے جبکہ میکسیکو کے لیے نارتھ اینڈ سینٹرل امریکن جسے CONCACAF کہتے ہیں وہ ہوتی ہے۔
اس کے بعد نمبر آتا ہے شرکت نہ کرنے والے ممالک کی ٹیموں کا۔ اس میں ظاہر ہے کہ ہم جنوبی ایشیا والے بہت نیچے ہوتے ہیں۔ اس وجہ سے مجھے ابتدائی طور پر اس میچ میں جانے کی اجازت نہیں ملی۔ یہ میرے لیے بہت بڑا جھٹکا تھا کیونکہ میرے ساتھ اس سے پہلے کبھی کسی بڑے میچ میں ایسا نہیں ہوا تھا۔
یہاں قطر میں ٹائمز آف انڈیا سے تعلق رکھنے والے میرے دوست سدھارتھ سکسینا اور دی ہندو سے تعلق رکھنے والے آیون داس گپتا ہیں اور ہم تینوں کو ہی اجازت نہیں ملی حالانکہ ہم سمجھتے ہیں کہ ہمارے اخبار بہت بڑے ہیں اور ہمیں اجازت ملنی چاہیے تھی لیکن ہم سب کو مسترد کردیا گیا تھا۔
فیفا نے ایک ویٹ لسٹ بھی رکھی ہوتی ہے کہ اگر آپ کو اجازت نہ ملے تو آپ اس ویٹ لسٹ کے لیے درخواست دے دیں۔ کیونکہ کبھی کبھی فیفا میچ کے لیے فین سیٹنگ میں سے بھی جگہ نکالتی ہے تو امکان ہوتا ہے کہ اس ویٹ لسٹ میں شامل لوگوں کو بھی اجازت مل جائے۔ ہم نے بھی ویٹ لسٹ کے لیے درخواست دے دی اور پھر بس ایک طویل انتظار تھا۔
کل صبح پولینڈ اور سعودی عرب کا میچ تھا۔ ہوتا یہ ہے کہ فیفا کی بس آپ کو ایک میچ ختم ہونے کے بعد دوسرے میچ کے لیے لے جاتی ہے، اب چونکہ ہمارے پاس دوسرے میچ کو کور کرنے کی اجازت نہیں تھی اس وجہ سے ہم نے ورچوئل اسٹیڈیم جانے کا فیصلہ کیا۔ فیفا نے اس مرتبہ ایک ورچوئل اسٹیڈیم بھی بنایا ہے جہاں آپ 4 مختلف زاویوں سے میچ دیکھ سکتے ہیں۔ جو صحافی اصل اسٹیڈیم نہیں جاتے وہ وہاں بیٹھ کر میچ کور کرلیتے ہیں۔
ہم واپس مین میڈیا سینٹر پہنچے اور ورچوئل اسٹیڈیم کی جانب جا ہی رہے تھے کہ میرا فون بجا۔ میں نے دیکھا کہ فیفا کی میل آئی ہوئی تھی کہ آپ کو میچ کور کی اجازت مل گئی ہے اور آپ اپنا ٹکٹ لے لیں۔ میں نے سدھارتھ سے کہا کہ وہ بھی اپنا فون دیکھیں کیونکہ ہم ایک ہی خطے میں آتے ہیں تو ہمارے فیفا کے معاملات بھی ایک ساتھ ہی ہوتے ہیں مگر انہوں نے فون دیکھا تو کوئی میل نہیں آئی تھی۔
ہم میڈیا ٹکٹنگ کاؤنٹر گئے اور میں نے اپنا ٹکٹ لیا۔ لیکن ساتھ کاؤنٹر پر موجود خاتون سے دریافت بھی کیا کہ سدھارتھ کا ٹکٹ کیوں نہیں آیا مگر ہمیں کوئی جواب نہیں ملا۔ بہرحال میں اسٹیڈیم کی جانب جانے لگا اور سدھارتھ ورچوئل اسٹیڈیم کی جانب کہ اتنے میں کاؤنٹر پر موجود خاتون نے مجھے آواز دے کر کہا آپ کے ساتھ جو تھے انہیں بلائیں، ان کا ٹکٹ بھی منظور ہوگیا ہے۔
یہ میسی کے لیے بہت اہم میچ تھا کیونکہ یا تو میسی اس میچ میں کچھ کرتا یا پھر میسی کی ٹیم گھر جاتی۔ اس میچ کو کور کرنے کے لیے برِصغیر سے صرف 3 صحافی اسٹیڈیم میں موجود تھے اور میں ان میں سے ایک تھا۔ میں خود کو خوش قسمت سمجھتا ہوں کہ میں نے یہ میچ براہِ راست دیکھا، یہ وہ لمحات ہوتے ہیں جو زندگی بھر یاد رہتے ہیں کہ آپ کس طرح اس میچ میں پہنچے۔
'''))

summaryApp()

        

