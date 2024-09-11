import google.generativeai as genai
import os


genai.configure(api_key="AIzaSyD0Svrt9-j2ORLSooAOB3jeM33PNi8SeNE")

model = genai.GenerativeModel(model_name = "gemini-1.5-flash")
#response = model.generate_content("Write a story about a magic backpack.")
#print(response.text)

import pandas as pd
import os
from tqdm.auto import tqdm  # this is our progress bar
import openai
#import spacy
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
from pinecone import Pinecone
import PyPDF2
import openai
import time


nl = "\n"


from pinecone import Pinecone

pc = Pinecone(api_key="d403ddc4-dc54-47d5-9c8f-ed19848d06ce")
index = pc.Index("final-asha")


def getQuotes(query, index):
    query = query
    MODEL = "text-embedding-3-small"

    xq = openai.Embedding.create(input=query, engine=MODEL)['data'][0]['embedding']

    res = index.query(vector = [xq], top_k=5, include_metadata=True)

    justQuotes = []
    for i in range(len(res['matches'])):
        justQuotes.append(res['matches'][i]['metadata']['text'])

    return justQuotes

def format_quotes(quotes):
    result = ""
    for i, quote in enumerate(quotes, start=1):
        result += f"quote {i} = {quote}\n"
    return result

def summarizeQuotes(query, quotes):
    finalQuery = query + nl + "Here is the evidence to pull from: " + nl + format_quotes(quotes)
    response = model.generate_content(finalQuery)
    return response.text

def geminiCall(query):
   response = model.generate_content(query)
   return response.text

def combine_dict_entries(input_output_dict):
    if not input_output_dict:
        return ""
    
    combined_string = ""
    separator = " Here is the next query and response "
    
    for key, value in input_output_dict.items():
        combined_string += f"Query {key} Response {value}{separator}"
    
    return combined_string


def promptGuidelinesFlow(index, pastDict):
    classificationStore = "Conditions, Results, Solutions, End"
    #Check to see if end or not
    done = False
    
    #Get initial variables
    role = "Imagine you’re a wise and attentive doctor giving advice to a community health worker (CHW) who is helping people. This is not a standard hospital and does not follow western medicine protocol. Assume your pretraining is not the ground truth but the information and quotes provided is. The CHW is in a 3rd world country and only has access to basic medical equipment. "
    
    #Get query
    if not pastDict:
      query = input("Hi I am a personal medical assistant. How may I help you today? (Enter STOP to end chat): ")
    else:
       query = input("\n")
       
    
    #Combine context to set up for classification
    contextClass1 = "Based on the input provided classify the text as one of these categories " + classificationStore
    contextClass2 = ". Make sure your response is only 1 word, the classification. For example if the classification is 'solutions' the output should only by 'solutions'. Do not add anything else. Here is the query to classify"
    combinedClass = contextClass1 + contextClass2 + query
    
    #Get classification and format it
    classifications = geminiCall(combinedClass)
    classifications = classifications.strip().lower()

    #Extra variables for the if/else as well as past chat
    classificationArray = ["conditions", "results", "solutions", "end"]
    pastChat = "Here is the previous chat log. Use this as context to better aid the CHW. " + combine_dict_entries(pastDict)
    
    
    #If else to check what class it is

    #Class conditions
    if (classifications == classificationArray[0]):
      contextCondition =  "Come up with medical tests to assess the condition of the patient. Do not suggest diagnosis or solutions. Only come up with tests and the CHW will report back to you the results of the test."
      combinedContext = role + "\n" + pastChat + contextCondition
      quote = getQuotes(combinedContext, index)
      finalSummary = summarizeQuotes(combinedContext, quote)
    
    #Class results
    elif (classifications == classificationArray[1]):
      contextResults = "These are the results of the test. Suggest only a diagnosis, not treatements or prevention methods. "
      combinedContext = role + "\n" + pastChat + contextResults
      quote = getQuotes(combinedContext, index)
      finalSummary = summarizeQuotes(combinedContext, quote)
    
    #Class solutions (get the solutions)
    elif (classifications == classificationArray[2]):
      contextSolutions = "Now suggest treatements and prevention methods, primarily home remedies and local natural resources. Do not suggest western medical solutions. "
      combinedContext = role + "\n" + pastChat + contextSolutions
      quote = getQuotes(combinedContext, index)
      finalSummary = summarizeQuotes(combinedContext, quote)
    
    #End 
    else:
       done = True
       print("Chat has ended")
       return -1
    
    #Check if you want to go again ---> call the function and update the previous values in the dictionary
    if (done == False):
       print("\n")
       print(finalSummary)
       pastDict[query] = finalSummary
       promptGuidelinesFlow(index, pastDict)
    else:
       return -1

pastDict = {}
promptGuidelinesFlow(index, pastDict)

#I am lightheaded and dizzy. I feel way too hot and nauseous

