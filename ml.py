import pandas as pd
from tqdm.auto import tqdm  # this is our progress bar
import openai
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
#Data imports
import pandas as pd
import numpy as np
#Pinecone imports
import pinecone
from pinecone import PodSpec
from pinecone import Pinecone
from pinecone import ServerlessSpec
#OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from pinecone import Pinecone
import PyPDF2
import openai


def getData(tokens, overlap, path):

  def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text

  # Replace "your_pdf_file.pdf" with the actual file name you uploaded
  pdf_path = path
  text = extract_text_from_pdf(pdf_path)

  def split_text_into_chunks(text, word, overlap):
    # Split the text into a list of words
    words = text.split()
    # Calculate the number of words in each chunk and the number of chunks
    chunk_size = int(word)
    num_chunks = int(len(words) / chunk_size) + 1
    # Calculate the number of overlapping words
    overlap_size = int(chunk_size * overlap)
    # Create a list to store the chunks
    chunks = []
    # Loop through the text and create the chunks
    for i in range(num_chunks):
        # Calculate the start and end indices for the current chunk
        start = i * chunk_size
        end = min((i + 1) * chunk_size, len(words))
        # If this is not the first chunk, add the overlapping words from the previous chunk
        if i > 0:
            start -= overlap_size
        # Create the chunk and add it to the list
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)
    return chunks

  tokens = tokens
  word = tokens * 0.75 #Constant proportion
  overlap = overlap #Number between 0-1 as a percent
  chunks = split_text_into_chunks(text, word, overlap)
  i = 0
  my_list = []
  for chunk in chunks:
      my_list.append(chunk)
  return my_list, extract_text_from_pdf(pdf_path)

def getIndex():
  pc = Pinecone(api_key="86f31e00-a5cc-438d-b95b-4089562e9b57")
  index = pc.Index("quickstart")
  return index

def upserts(q, values, index):
  index = index
  my_list = values

  query = q
  MODEL = "text-embedding-3-small"

  res = openai.Embedding.create(
      input=[query], engine=MODEL
  )

  embeds = [record['embedding'] for record in res['data']]

  # load the first 1K rows of the TREC dataset
  #trec = load_dataset('trec', split='train[:1000]')

  batch_size = 32  # process everything in batches of 32
  for i in tqdm(range(0, len(my_list), batch_size)):
      # set end position of batch
      i_end = min(i+batch_size, len(my_list))
      # get batch of lines and IDs
      lines_batch = my_list[i: i+batch_size]
      ids_batch = [str(n) for n in range(i, i_end)]
      # create embeddings
      res = openai.Embedding.create(input=lines_batch, engine=MODEL)
      embeds = [record['embedding'] for record in res['data']]
      # prep metadata and upsert batch
      meta = [{'text': line} for line in lines_batch]
      to_upsert = zip(ids_batch, embeds, meta)
      # upsert to Pinecone
      index.upsert(vectors=list(to_upsert))

def getRes(query, index):
  query = query
  MODEL = "text-embedding-3-small"

  xq = openai.Embedding.create(input=query, engine=MODEL)['data'][0]['embedding']

  res = index.query(vector = [xq], top_k=10, include_metadata=True)

  return res

def vectorQuotes(query, index):
  similarity = getRes(query, index)
  #justQuotes just uses what the query results from Pinecone itself
  justQuotes = []
  for i in range(len(similarity['matches'])):
    justQuotes.append(similarity['matches'][i]['metadata']['text'])
  return justQuotes

import openai

def getFinalSummaryGPT4(my_list, queryContext):
  my_list = my_list
  queryContext = queryContext

  # Function to split a list into equal sublists
  def split_list(lst, num_sublists):
      avg = len(lst) // num_sublists
      remainder = len(lst) % num_sublists
      return [lst[i * avg + min(i, remainder):(i + 1) * avg + min(i + 1, remainder)] for i in range(num_sublists)]

  # Split 'my_list' into n equal sublists
  n = 5
  sublists = split_list(my_list, n)

  # Generate summaries for each sublist using the OpenAI API
  sublist_summaries = []

  for i, sublist in enumerate(sublists):
      sublist_text = ' '.join(sublist)
      response = openai.ChatCompletion.create(
        model="gpt-4",
        temperature=0.9,
        top_p=0.9,
        messages= [{ "role": "user", "content": queryContext+sublist_text }] )

      # Extract the summary from the API response
      summary = response.choices[0].message.content
      sublist_summaries.append(summary)

  # Combine the 10 summaries into one variable
  combined_summary = ' '.join(sublist_summaries)

  # Add a specific prompt tailored to your data
  specific_prompt = f"Given the following summaries:\n{combined_summary}\n\nGenerate a coherent final summary that captures the essence of the provided information."

  specific_prompt = queryContext + specific_prompt
  # Use OpenAI API to generate the final coherent summary

  response_combined = openai.ChatCompletion.create(
      model="gpt-4",
      temperature=0.9,
      top_p=0.9,
      messages= [{ "role": "user", "content": specific_prompt}] )

  # Extract the final summary from the API response
  final_summary = response_combined.choices[0].message.content.strip()

  return final_summary
from pymongo import MongoClient

# Direct inclusion of sensitive information (Not Recommended for production)
mongo_uri = "mongodb+srv://mabhi02:AVMavmAVM@avmscluster.9vuoubd.mongodb.net/?retryWrites=true&w=majority&appName=AVMsCluster"

# Initialize MongoDB connection
client = MongoClient(mongo_uri)
db = client['myDatabase']
collection = db['questions']

def save_question_answer(ui_prompt, response_quotes):
    """
    Save the question and its answer to MongoDB.
    """
    try:
        question_document = {
            "prompt": ui_prompt,
            "response": response_quotes
        }
        result = collection.insert_one(question_document)
        print(f"Document inserted with id: {result.inserted_id}")
    except Exception as e:
        print(f"An error occurred while inserting the document: {e}")

def fetch_questions_answers():
    """
    Fetch all questions and answers from MongoDB.
    """
    try:
        questions = collection.find()
        for question in questions:  
            print(f"Prompt: {question['prompt']}, Response: {question['response']}")
    except Exception as e:
        print(f"An error occurred while fetching the documents: {e}")

def AVM(ui_prompt):
    """
    Process the prompt using OpenAI and store the result in MongoDB.
    """
    try:
        query = ui_prompt
        #upserts(query, my_list, index) --> run if change tokens and overlap
        context = "Based solely the following information answer the question. Take into account all the important quotes that answer the question"
        responseQuotes = getFinalSummaryGPT4((vectorQuotes((query + context), getIndex())), (query + context))
        #save_question_answer(ui_prompt, responseQuotes)
        return responseQuotes


    except Exception as e:
        print(f"An error occurred in ML function: {e}")
        return []

# Running the ML function with a sample prompt
"""
var = 4
ux = 0
while ux < var:
    inp = input("enter: ") 
    varr = AVM(inp)
    print('Question is:', inp)
    print("Answer is:", varr)
    ux += 1
"""
#ui_prompt = 'where do I go if the hospital shant be open'
