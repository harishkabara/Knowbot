def nlp(sentence):
    import nltk
    import string
    import json
    import pymongo
    from difflib import SequenceMatcher
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords, wordnet
    from nltk.stem import WordNetLemmatizer
    from pymongo import MongoClient
    from nltk.metrics import edit_distance
    from NLPmongo import nlpmongo
    from nltk.corpus import words

    def get_wordnet_pos(word):
        tag = nltk.pos_tag([word])[0][1][0].upper()
        tag_dict = {"J": wordnet.ADJ,
                    "N": wordnet.NOUN,
                    "V": wordnet.VERB,
                    "R": wordnet.ADV}
        return tag_dict.get(tag, wordnet.NOUN)

    def get_pos(word):
        tag = nltk.pos_tag([word])[0][1][0].upper()
        tag_dict = {"J": wordnet.ADJ,
                    "N": wordnet.NOUN,
                    "V": wordnet.VERB,
                    "R": wordnet.ADV}
        return tag_dict.get(tag)
    lemantizer = WordNetLemmatizer()
    s = str(sentence)
    spellcheck={}
    prem_tokens=[]
    s = s.lower()
    word = word_tokenize(s)
    i=0
    for x in word:
       prem_tokens.append(x)
       i=i+1
       spellcheck[i]=x
    lemantized_output = ' '.join([lemantizer.lemmatize(q, get_wordnet_pos(q)) for q in word])
    word = word_tokenize(lemantized_output)
    exclude = set(string.punctuation)
    x = ' '.join(ch for ch in prem_tokens if ch not in exclude)
    w = ' '.join(ch for ch in word if ch not in exclude)
    print(w)
    word = word_tokenize(w)
    prem_tokens=word_tokenize(x)
    whins = " "
    whwords = ["who", "why", "what", "where", "how", "when", "which"]
    for token in word:
        if token in whwords:
            whins = token
    clean_tokens = word[:]
    sr = stopwords.words('english')
    for token in word:
        if token in stopwords.words('english'):
            clean_tokens.remove(token)
    same_dict1=[]
    same_dict11=[]
    client = MongoClient('localhost', 27017)
    db = client['KnowBot']
    collection = db['token']
    collection1=db['spellcheck']
    token_dict= collection.find()
    token_dict1=collection1.find()
    for tok in token_dict:
        same_dict1.append(tok.get("token"))
    for tok1 in token_dict1:
        same_dict11.append(tok1.get("word"))
    print(same_dict1)
    print(clean_tokens)
    clean_tokens.append(whins)
    print(clean_tokens)
    clean_tokens1=[]
    for x in clean_tokens:
        clean_tokens1.append(x)
    i = []
    if clean_tokens.__len__() == 0:
        answerjson = collection.find({"whword": whins})
    else:
        spellcheckupdated={}
        i = 1
        while i <= spellcheck.__len__():
            word = spellcheck.get(i)
            spellcheckupdated[i]=word
            i=i+1
        for same1 in prem_tokens:
            temp_word1 = same1
            temp = 0.7
            for dict1 in same_dict11:
                perc1 = SequenceMatcher(None, same1, dict1).ratio()
                if perc1 >= temp:
                    temp = perc1
                    temp_word1 = dict1
            spellcheck = spellcheck_func(temp_word1, spellcheck)
        for same in clean_tokens:
            temp_word = same
            temp = 0.7
            for dict in same_dict1:
                perc = SequenceMatcher(None, same, dict).ratio()
                if perc >= temp :
                    temp = perc
                    temp_word = dict

            clean_tokens1.remove(same)
            clean_tokens1.append(temp_word)

        i = 1
        ultimatestr=""
        while i <= spellcheck.__len__():
            word = spellcheck.get(i)
            ultimatestr=ultimatestr+" "+word
            i = i + 1
        if spellcheck == spellcheckupdated:
            spellflag = "Correct"
        else:
            spellflag = "Incorrect"
        result = nlpmongo(clean_tokens1)
        print(result)
        if result.get("question")== None:
            result= result.get("answer")
            ans={"answer":result,"spell":spellflag,"correctedquestion":ultimatestr}
        else:
            question1 = result.get("question")
            count =  result.get("questioncount")
            ans={"question":question1,"count":count,"spell":spellflag,"correctedquestion":ultimatestr}
    print(ans)
    return ans
def spellcheck_func(temp,spellcheck):
    from difflib import SequenceMatcher
    from nltk.metrics import edit_distance
    i=1
    while i <= spellcheck.__len__():
        same = spellcheck.get(i)
        threshold_perc = 0.7
        perc = SequenceMatcher(None, same, temp).ratio()
        if perc >= threshold_perc:
           spellcheck.update({i:temp})
        i=i+1
    return spellcheck
def userloginsert(question,userid):
    from pymongo import MongoClient
    flag="N"
    client = MongoClient('localhost', 27017)
    db = client['KnowBot']
    collection1 = db['user_questions']
    existingques=collection1.find()
    for item in existingques:
        if item.get('question')== question:
            flag="Y"
            break
    if flag!="Y":
      collection1.insert({"question":question,"user_id":userid,"feedback":"false"})

def feedback(answer,score,userid):
    from pymongo import MongoClient
    import math
    import ast
    import json
    r = 0.5
    n = 0
    sumlike=0
    sumdislike=0
    client = MongoClient('localhost', 27017)
    db = client['KnowBot']
    collection = db['NLPdb']
    collection1 = db['user_questions']
    print(score)
    resultset=collection.find({"answer":answer,"idscore.id":userid})
    if resultset.count()==0:
        if score == 1:
          collection.update({"answer": answer},{"$push": {"idscore": {"id": userid, "like": 1, "dislike": 0}}})
        else:
            collection.update({"answer": answer}, {"$push": {"idscore": {"id": userid, "like": 0, "dislike": 1}}})
    else:
        count=0
        for result in resultset:
            idscore = result.get("idscore")
            for items in idscore:
                user_id=items.get("userid")
                count = count + 1
                if user_id == userid:
                    likescore=float(items.get("like"))
                    dislikescore=float(items.get("dislike"))
                    if score == 1:
                      sum = likescore
                      n = (math.log(1 - sum * (1 - r)) / math.log(r))
                      n = n + 1
                      if likescore == 0:
                          likescoreupdated=1
                          likescoreupdated=str(likescoreupdated)
                      else:
                          likescoreupdated = str((1 - math.pow(r,n))/(1 -r))
                      strcount= str(count-1)
                      query= "'idscore."+ strcount + ".like'"
                      queryupdate1= "{'answer':'" + answer + "','idscore.userid':'" + userid + "'}"
                      queryupdate2="{'$set': {" + query + ":'" + likescoreupdated + "'}}"
                      jsonquery1 = ast.literal_eval(queryupdate1)
                      jsonquery2 = ast.literal_eval(queryupdate2)
                      collection.update(jsonquery1,jsonquery2)
                    else:
                        sum = dislikescore
                        n = (math.log(1 - sum * (1 - r)) / math.log(r))
                        n = n + 1
                        if dislikescore == 0:
                            dislikescoreupdated = 1
                            dislikescoreupdated=str(dislikescoreupdated)
                        else:
                            dislikescoreupdated = str((1 - math.pow(r, n)) / (1 - r))
                        strcount = str(count - 1)
                        query = "'idscore." + strcount + ".dislike'"
                        queryupdate1 = "{'answer':'" + answer + "','idscore.userid':'" + userid + "'}"
                        queryupdate2 = "{'$set': {" + query + ":'" + dislikescoreupdated + "'}}"
                        jsonquery1 = ast.literal_eval(queryupdate1)
                        jsonquery2 = ast.literal_eval(queryupdate2)
                        collection.update(jsonquery1, jsonquery2)
    baseresultset = collection.find({"answer": answer})
    for base in baseresultset:
      ques = base.get('question')
    likepercen = percentcalc(answer)
    dislikepercen = 100 - likepercen
    for result in resultset:
       idscore = result.get("idscore")
       if idscore.__len__() - 1 >= 5:
        if dislikepercen >= 70:
            #collection.delete_one({"answer": answer})
            collection1.insert({"question": ques, "answer": answer, "feedback": "true"})

def percentcalc(answer):
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client['KnowBot']
    collection = db['NLPdb']
    sumlike=0
    sumdislike=0
    baseresultset = collection.find({"answer": answer})
    for base in baseresultset:
        idscore = base.get("idscore")
        for items in idscore:
            like = float(items.get("like"))
            dislike = float(items.get("dislike"))
            sumlike = sumlike + like
            sumdislike = sumdislike + dislike
    likepercen = (sumlike / (sumlike + sumdislike)) * 100
    likepercen = int(likepercen)
    return likepercen
def likedislikecount(answer):
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client['KnowBot']
    collection = db['NLPdb']
    baseresultset = collection.find({"answer": answer})
    likecount=0
    dislikecount=0
    for base in baseresultset:
        idscore = base.get("idscore")
        for items in idscore:
            like = float(items.get("like"))
            dislike = float(items.get("dislike"))
            if like !=0:
                likecount = likecount + 1
            if dislike !=0:
                dislikecount = dislikecount + 1
    countarray={"like":likecount,"dislike":dislikecount}
    return countarray
def wikiapicall(question):
    import requests
    import nltk
    import string
    import json
    import pymongo
    from difflib import SequenceMatcher
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords, wordnet
    from nltk.stem import WordNetLemmatizer
    from pymongo import MongoClient
    from nltk.metrics import edit_distance
    from NLPmongo import nlpmongo
    from nltk.corpus import words
    # find those words that may be misspelled

    def get_wordnet_pos(word):
        tag = nltk.pos_tag([word])[0][1][0].upper()
        tag_dict = {"J": wordnet.ADJ,
                    "N": wordnet.NOUN,
                    "V": wordnet.VERB,
                    "R": wordnet.ADV}
        return tag_dict.get(tag, wordnet.NOUN)

    def get_pos(word):
        tag = nltk.pos_tag([word])[0][1][0].upper()
        tag_dict = {"J": wordnet.ADJ,
                    "N": wordnet.NOUN,
                    "V": wordnet.VERB,
                    "R": wordnet.ADV}
        return tag_dict.get(tag)

    lemantizer = WordNetLemmatizer()
    s = str(question)
    s = s.lower()
    word = word_tokenize(s)
    i = 0
    lemantized_output = ' '.join([lemantizer.lemmatize(q, get_wordnet_pos(q)) for q in word])
    word = word_tokenize(lemantized_output)

    exclude = set(string.punctuation)
    w = ' '.join(ch for ch in word if ch not in exclude)
    print(w)
    word = word_tokenize(w)
    clean_tokens = word[:]
    sr = stopwords.words('english')
    string1=""
    for token in word:
        if token in stopwords.words('english'):
            clean_tokens.remove(token)
    same_dict1 = []
    clean_tokens1=[]
    for x in clean_tokens:
        clean_tokens1.append(x)
    client = MongoClient('localhost', 27017)
    db = client['KnowBot']
    collection = db['spellcheck']
    token_dict = collection.find()
    for tok in token_dict:
        same_dict1.append(tok.get("word"))
    for same in clean_tokens:
            temp_word = same
            temp = 0.9
            for dict in same_dict1:
                perc = SequenceMatcher(None, same, dict).ratio()
                if perc >= temp :
                    temp = perc
                    temp_word = dict

            clean_tokens1.remove(same)
            clean_tokens1.append(temp_word)
    for tokens in clean_tokens1:
        if string1=="":
            string1=tokens
        else:
            string1= string1+"%20"+tokens
    # response= requests.put("http://10.245.118.57:5000/user/feedback",json={"answer":"During this phase, the investors are pre-dominantly in their pre-retirement or retirement phase and they must rely on their accumulated assets for income generation.","score":1,"userid":"cg091188"})
    api1 = "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch="+string1+"&format=json"
    print(api1)
    response=requests.get(api1)
    a = response.json()
    count=0
    apire=[]
    for x in a.get("query").get("search"):
      if count<3:
        search = x.get("title")
        api = "https://en.wikipedia.org/w/api.php?action=opensearch&search=" + search + "&limit=1&format=json"
        response1 = requests.get(api)
        apicount=0
        for all in response1.json():
            if apicount!=0:
              for dual in all:
                apire.append(dual)
            apicount=apicount+1
        count=count+1
    return apire

def investopediacall(question):
    import requests
    import nltk
    import string
    import json
    import pymongo
    from difflib import SequenceMatcher
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords, wordnet
    from nltk.stem import WordNetLemmatizer
    from pymongo import MongoClient
    from nltk.metrics import edit_distance
    from NLPmongo import nlpmongo
    from nltk.corpus import words
    #from spellchecker import SpellChecker
    import ast
    from itertools import combinations
    import math
    client = MongoClient('localhost', 27017)
    db = client['KnowBot']
    collection = db['investwords']
    tokenlist=[]
    tokencursor=collection.find()
    for eachcursor in tokencursor:
        tokenlist.append(eachcursor.get("word"))
    # find those words that may be misspelled

    def get_wordnet_pos(word):
        tag = nltk.pos_tag([word])[0][1][0].upper()
        tag_dict = {"J": wordnet.ADJ,
                    "N": wordnet.NOUN,
                    "V": wordnet.VERB,
                    "R": wordnet.ADV}
        return tag_dict.get(tag, wordnet.NOUN)

    def get_pos(word):
        tag = nltk.pos_tag([word])[0][1][0].upper()
        tag_dict = {"J": wordnet.ADJ,
                    "N": wordnet.NOUN,
                    "V": wordnet.VERB,
                    "R": wordnet.ADV}
        return tag_dict.get(tag)

    lemantizer = WordNetLemmatizer()
    s = str(question)
    s = s.lower()
    word = word_tokenize(s)
    i = 0
    lemantized_output = ' '.join([lemantizer.lemmatize(q, get_wordnet_pos(q)) for q in word])
    word = word_tokenize(lemantized_output)
    exclude = set(string.punctuation)
    w = ' '.join(ch for ch in word if ch not in exclude)
    print(w)
    word = word_tokenize(w)
    clean_tokens = word[:]
    clean_tokens1=[]
    sr = stopwords.words('english')
    same_dict1=tokenlist
    for token in word:
        if token in stopwords.words('english'):
            clean_tokens.remove(token)
    for x in clean_tokens:
        clean_tokens1.append(x)
    for same in clean_tokens:
        temp_word = same
        temp = 0.7
        for dict in same_dict1:
            perc = SequenceMatcher(None, same, dict).ratio()
            if perc >= temp:
                temp = perc
                temp_word = dict

        clean_tokens1.remove(same)
        clean_tokens1.append(temp_word)
    urllist=[]
    count=0
    result = {}
    client = MongoClient('localhost', 27017)
    db = client['KnowBot']
    collection1 = db['investtoken']
    sumtotcount = collection1.find().count()
    tokenlist = clean_tokens1
    counttokenlist = tokenlist.__len__()
    temptoken = ""
    for ls in tokenlist:
        if temptoken == "":
            temptoken = "{'TOKEN':'" + ls + "'"
        else:
            temptoken = temptoken + "},{'TOKEN':'" + ls + "'"

    x1 = temptoken + "}"
    x2 = "{'$or':[" + x1 + "]}"
    b = ast.literal_eval(x2)
    a = collection1.find(b)
    questionlist = []
    scorelist = []
    typeque = []
    for x in a:
        arr = x.get("TOKEN")
        ques = x.get("URL")
        print(ques)
        sum = 0
        count = 0
        for tok in tokenlist:
            idf = 0
            if tok in arr:
                cou = int(collection1.find({"TOKEN": tok}).count())
                rever = sumtotcount / cou
                idf = math.log(rever)
                entry=collection1.find({"URL": ques})
                tokcount=0
                tokenlistdb=[]
                for one in entry:
                    tokenlistdb=one.get("TOKEN")


                for to in tokenlistdb:
                    if to==tok:
                        tokcount=tokcount+1

                tokendensity=  int(tokcount)/100
                tdidf= idf * tokendensity
                sum = sum + tdidf
                count = count + 1
        tf = count / counttokenlist
        score = tf * sum
        print(score)
        questionlist.append(ques)
        scorelist.append(score)
    count = 0
    topthree = sorted(zip(scorelist, questionlist), reverse=True)[:10]
    for top in topthree:
        count = count + 1
        qu = top.__getitem__(1)
        typeque.append(qu)
    result = {"links": typeque, "linkcount": count}
    return result
