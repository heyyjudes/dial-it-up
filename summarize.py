from nltk.corpus import brown
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))
import numpy as np
import gensim
import scipy.spatial as sp 
from scraper import extractText, findSummary 
from occamy import Socket

def find_top_sent(model, target_word, url): 
    # REPLACE WITH READ DICT
    # with open('sample.txt', 'r') as f: 
    #     lines = f.readlines() 

    # lines = [l.rstrip("\n") for l in lines if l != '\n']
    
    # #preprocess
    # sentences = " ".join(lines[2:])

    sentences = extractText(url)["text"]
    sentences = sent_tokenize(sentences)
    tokenized_sents = [] 
    for s in sentences: 
        word_arr = word_tokenize(s)
        for w in word_arr: 
            if w in stop_words: 
                word_arr.remove(w)
        tokenized_sents.append(word_arr)

        #build freq_dict 
    sent_score = []
    w_target = model[target_word]
    for s in tokenized_sents: 
        s_score = 0 
        for w in s: 
            try: 
                dist = 1 - sp.distance.cosine(model[w], w_target)
            # TODO: add word2vec
    #         if w == target_word: 
    #             s_score += 1
                s_score += dist
            except: 
                s_score += 0 
        s_score /= len(s)
        sent_score.append(s_score)

    ranking = np.argsort(sent_score)
    top_10_rank = list(ranking[-4:]) 
    top_10_rank.reverse()
    top_10_sents = [] 

    output_sentences = [] 
    for i in top_10_rank: 
        # print(sentences[i]) 
        # print(sent_score[i])
        if i+1 < len(sentences): 
            output_sentences.append(sentences[i] + '\t' + sentences[i+1] + '\t' + sentences[i+2])
        else: 
            output_sentences.append([sentences[i]]) 
    return '\n'.join(output_sentences) 

def call_channel(msg, x):
    return msg["body"]

class Message: 
    def __init__(self): 
        self.init_msg = None 
        self.query_msg = None 

    def set_init_msg(self, msg_str): 
        self.init_msg = msg_str

    def set_query_msg(self, msg_str): 
        self.query_msg = msg_str

if __name__ == "__main__": 
    model = gensim.models.KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)
   
    socket = Socket("ws://dlevs.me:4000/socket")
    socket.connect()

    s_msg = Message() 

    channel = socket.channel("room:lobby", {})
    channel.on("connect", print('Im in'))
    channel.on("initiate", lambda msg, x: s_msg.set_init_msg(msg["body"]))
    channel.on("question", lambda msg, x:s_msg.set_query_msg(msg["body"]))

    channel.join()

    print("Enter your message and press return to send the message.")
    print()
    url = 'https://www.nytimes.com/2018/06/09/science/fish-decompression-chamber.html?action=click&contentCollection=science&region=rank&module=package&version=highlights&contentPlacement=2&pgtype=sectionfront'

    while s_msg.init_msg == None: 
        pass 
    print(s_msg.init_msg)

    result = extractText(url)["text"]
    abs_sum = findSummary(result, 0.1)
    
    channel.push("questionRESULT", {"body": '1 ' + abs_sum}) 

    while True: 
        while s_msg.query_msg == None: 
            pass 

        print(s_msg.query_msg)
        word = s_msg.query_msg.split("_")[-1]
        try : 
            output_sents = find_top_sent(model, word, url)
            channel.push("questionRESULT", {"body": '1 ' + output_sents}) 
            s_msg.query_msg = None 
        except: 
            print("sentence not found")


