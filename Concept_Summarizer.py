import streamlit as st
import bs4 as bs
import urllib.request
import re
import nltk
import heapq
from PyPDF2 import PdfFileReader
import fitz

def summarize_article(link, a, b):
    scraped_data = urllib.request.urlopen(link)
    article = scraped_data.read()
    parsed_article = bs.BeautifulSoup(article, 'lxml')
    paragraphs = parsed_article.find_all('p')
    article_text = ""
    for p in paragraphs:
        article_text += p.text
    article_text = re.sub(r'\[[0-9]*\]', ' ', article_text)
    article_text = re.sub(r'\s+', ' ', article_text)
    formatted_article_text = re.sub('[^a-zA-Z]', ' ', article_text)
    formatted_article_text = re.sub(r'\s+', ' ', formatted_article_text)
    sentence_list = nltk.sent_tokenize(article_text)
    stopwords = nltk.corpus.stopwords.words('english')
    word_frequencies = {}
    for word in nltk.word_tokenize(formatted_article_text):
        if word not in stopwords:
            if word not in word_frequencies.keys():
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1
    maximum_frequncy = max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word] / maximum_frequncy)
    sentence_scores = {}
    for sent in sentence_list:
        for word in nltk.word_tokenize(sent.lower()):
            if word in word_frequencies.keys():
                if len(sent.split(' ')) < a:
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_frequencies[word]
                    else:
                        sentence_scores[sent] += word_frequencies[word]
    summary_sentences = heapq.nlargest(b, sentence_scores, key=sentence_scores.get)
    summary = ' '.join(summary_sentences)
    return summary

def text_summary(text, a, b):
    sentences = nltk.sent_tokenize(text)
    word_frequencies = {}
    for sentence in sentences:
        words = nltk.word_tokenize(sentence)
        for word in words:
            if word not in nltk.corpus.stopwords.words('english'):
                if word not in word_frequencies.keys():
                    word_frequencies[word] = 1
                else:
                    word_frequencies[word] += 1
    maximum_frequncy = max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word] / maximum_frequncy)
    sentence_scores = {}
    for sentence in sentences:
        for word in nltk.word_tokenize(sentence.lower()):
            if word in word_frequencies.keys():
                if len(sentence.split(' ')) < a:
                    if sentence not in sentence_scores.keys():
                        sentence_scores[sentence] = word_frequencies[word]
                    else:
                        sentence_scores[sentence] += word_frequencies[word]
    summary_sentences = heapq.nlargest(b, sentence_scores, key=sentence_scores.get)
    summary = ' '.join(summary_sentences)
    return summary



def extract_text_from_pdf(file_path, a, b):
    text = ""
    with fitz.open(file_path) as pdf:
        for page_num in range(len(pdf)):
            page = pdf.load_page(page_num)
            text += page.get_text()
    return text


st.sidebar.title("Options")
choice = st.sidebar.radio("Choose an option:", ("Summarize URL", "Summarize Text", "Summarize Document"))

if choice == "Summarize URL":
    st.header("Summarize URL")
    links = st.text_input("Enter the URL:")
    
    size = st.radio("Select Summarization Size:", ("Small", "Medium", "Large"))

    if size == "Small":
        a = 10
        b = 5
    elif size == "Medium":
        a = 100
        b = 30
    else:
        a = 10000
        b = 1000

    if st.button("Summarize"):
        if links:
            summary = summarize_article(links, a, b)
            st.write(summary)
        else:
            st.write("Please enter a URL.")

elif choice == "Summarize Text":
    st.header("Summarize Text")
    input_text = st.text_area("Enter your text here")
    if input_text is not None:
        size = st.radio("Select Summarization Size:", ("Small", "Medium", "Large"))

        if size == "Small":
            a = 10
            b = 5
        elif size == "Medium":
            a = 100
            b = 30
        else:
            a = 10000
            b = 1000

        if st.button("Summarize Text"):
            col1, col2 = st.columns([1,1])
            with col1:
                st.markdown("**Your Input Text**")
                st.info(input_text)
            with col2:
                st.markdown("**Summary Result**")
                result = text_summary(input_text, a, b)
                st.success(result)

elif choice == "Summarize Document":
    st.header("Summarize Document")
    input_file = st.file_uploader("Upload your document here", type=['pdf'])
    a, b = 100, 30  # Default values for a and b
    if input_file is not None:
        size = st.radio("Select Summarization Size:", ("Small", "Medium", "Large"))

        if size == "Small":
            a = 10
            b = 5
        elif size == "Medium":
            a = 100
            b = 30
        else:
            a = 10000
            b = 1000

        if st.button("Summarize Document"):
            with open("doc_file.pdf", "wb") as f:
                f.write(input_file.getbuffer())
            col1, col2 = st.columns([1,1])
            with col1:
                st.info("File uploaded successfully")
                extracted_text = extract_text_from_pdf("doc_file.pdf", a, b)
                st.markdown("**Extracted Text is Below:**")
                st.info(extracted_text)
            with col2:
                st.markdown("**Summary Result**")
                text = extract_text_from_pdf("doc_file.pdf", a, b)
                doc_summary = text_summary(text, a, b)
                st.success(doc_summary)
