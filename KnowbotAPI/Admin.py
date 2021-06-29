message=""
from pymongo import MongoClient
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
import string
#import math
client = MongoClient('localhost', 27017)
db = client['KnowBot']
collection = db['NLPdb']
collection1 = db['token']
collection2 = db['user_questions']
collection3=db['admin']
collection4=db['deleted_entries']
collection5=db['spellcheck']
def get_wordnet_pos(word):
    import nltk
    from nltk.corpus import stopwords, wordnet
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}
    return tag_dict.get(tag, wordnet.NOUN)

def insertintoword(q1):
    lemantizer = WordNetLemmatizer()
    sentence = q1
    s = str(sentence)
    s = s.lower()
    word = word_tokenize(s)
    exclude = set(string.punctuation)
    w = ' '.join(ch for ch in word if ch not in exclude)
    word = word_tokenize(w)
    clean_tokens = word[:]
    for token in clean_tokens:
        print(token)
        records_present = collection5.find({"word": token})
        if records_present.count()==0:
            collection5.insert_one({"word":token})

def tokenization(sentence):

    lemantizer = WordNetLemmatizer()
    # sentence = "What are the different phases of Wealth Management?"
    s = str(sentence)
    s = s.lower()
    word = word_tokenize(s)
    lemantized_output = ' '.join([lemantizer.lemmatize(q, get_wordnet_pos(q)) for q in word])
    word = word_tokenize(lemantized_output)
    exclude = set(string.punctuation)
    w = ' '.join(ch for ch in word if ch not in exclude)
    word = word_tokenize(w)
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
    clean_tokens.append(whins)
    print(clean_tokens)
    return clean_tokens
def getIDFScore(token):
    import math
    resultset=collection.find()
    totalrecord=resultset.count()
    tokencount=0
    for result in resultset:
        if token in result.get("token"):
            tokencount=tokencount+1

    ratio=totalrecord/tokencount
    score=math.log(ratio)
    return score
def updatetokentable(tokens):
    for token in tokens:
        score=getIDFScore(token)
        result=collection1.find()
        for res in result:
            print(res)
        exist_record=collection1.find({"token": token})
        try:
            records_updated = collection1.update_one({"token": token},{"$set":{"IDFScore": score}})
            if records_updated.modified_count > 0:
                print("IDF score updated for "+token+" with"+str(score))
            elif exist_record.count()>0:
                print("token already exist with same IDFScore, nothing to update")
            else:
                collection1.insert({"token":token,"IDFScore":score})
                print("record created for token-" + token + " with-" + str(score))
        except BaseException as e:
            print(str(e))

def downloadtask():
    resultset=collection.find()
    return resultset
def downloadfeedback():
    resultset=collection2.find({"feedback":"true"})
    return resultset
def feedbackcount():
    resultset=collection2.find({"feedback":"true"})
    return resultset.count()
def downloadunanswered():
    resultset=collection2.find({"feedback":"false"})
    return resultset
def unansweredcount():
    resultset=collection2.find({"feedback":"false"})
    return resultset.count()
def admintask(sentence):
    import string
    import json
    import ast
    import sys
    record_updated = 0
    records_created = 0
    try:
        try:
            body = ast.literal_eval(json.dumps(sentence))
        except:
            return "question/answer body either not available or in bad shape"+sys.exc_info()[0], 400


        # Updating the user
        ques = sentence.get("question")
        answer = sentence.get("answer")
        admin_id=sentence.get("userId")
        clean_tokens = tokenization(ques)
        #result=collection.find()
       # for res in result:
           # print(res)
        records_present=collection.find({"question": ques})
        records_updated = collection.update_one({"question": ques},{"$set":{"answer":answer,"token":clean_tokens,"admin_id":admin_id,  "idscore" : [ {"userid" : "admin","like" : "0","dislike" : "0"}]}})





        #result=collection.update_one()


        # Check if resource is updated
        if records_updated.modified_count > 0:
            message= "1 Record has been updated"
            record_updated= record_updated+1
        elif records_present.count()==0:
            message=insertintotable(sentence)

        else:
            message="Record already exist for this question-nothing to add/update"
        response_token=updatetokentable(clean_tokens)
        print (response_token)
        return (message)
    except BaseException as e:
        message= "Error occurred at the time of record updating-"+ str(e)
        #insertintotable(sentence)
        return (message)



def insertintotable(sentence):
    import json
    import ast
    #collection.insert(sentence)
    try:
        # Create new users
        try:
            body = ast.literal_eval(json.dumps(sentence))
        except:
            # Bad request as request body is not available
            # Add message for debugging purpose
            return "question/answer body either not available or in bad shape", 400
        ques = sentence.get("question")
        answer = sentence.get("answer")
        admin_id=sentence.get("userId")
        clean_token=tokenization(ques)
        array={'userid':'admin','like':'0','dislike':'0'}
        record_created = collection.insert({"question":ques,"answer":answer,"token":clean_token,"customer_score":10,"admin_id":admin_id,"idscore":[array]})
        #record_deleted=collection1.delete_one({"question":ques})
        message= "1 New record created"
        insertintoword(ques)
        resords_usertable=collection2.find({"question": ques})
        if resords_usertable.count()>0:
            collection2.delete_one({"question": ques})
        return message
    except BaseException as e:
        # Error while trying to create the resource
        # Add message for debugging purpose
        message= "Error occurred at the time of record creation-"+str(e)
        return message

def searchquestion(req):
    print("inside search question")
    searched_string=req.get("question")
    resultset=collection.find()
    count=0
    response="result|"
    for res in resultset:
        ques=res.get("question")
        if searched_string.lower() in ques.lower():
            response=response+","+ques
            count=count+1

    if(count==0):
        response = response + "," + "Question not available"
    return response

def getanswers(req):
    searched_string=req.get("question")
    resultset=collection.find({"question":searched_string})
    return resultset
def user_info():
    resultset=collection3.find({"active":"true"})
    return resultset
def delete_question(req):
    ques=req.get("question")
    ans=req.get("answer")
    user_id=req.get("userId")
    collection.delete_one({"question":ques})
    collection4.insert({"question":ques,"answer":ans,"user_id":user_id})
    return "Record deleted successfully for question-"+ques

def delete_users(req):
    users=req.get("users")
    userid=req.get("userId")
    userlist=users.split(",")
    for user in userlist:
        if not user==0:
            collection3.update_one({"admin_id":user},{"$set":{"active":"false","updated_by":userid}})

    return "User(s) deleted successfully"

def add_user(req):
    user_id=req.get("userIdValue")
    updated_id=req.get("systemname")
    name=req.get("userNameValue")
    resultset=collection3.find({"admin_id":user_id})
    if resultset.count()>0:
        collection3.update_one({"admin_id": user_id},{"$set":{"active":"true","updated_by":updated_id}})
    else:
        collection3.insert({"admin_id":user_id,"name":name,"updated_by":updated_id,"active":"true"})

    return "User added successfully with user_id-"+user_id

def check_admin(req):
    user_id=req.get("userId")
    resultset = collection3.find({"admin_id":user_id,"active":"true"})
    if(resultset.count()>0):
        return "true"
    else:
        return "false"

def validate_superadmin(req):
    user_id=req.get("UserId")
    password= req.get("Password")
    resultset = collection3.find({"admin_id":user_id})
    for res in resultset:
        act_pass=res.get("password")
    if(resultset.count()==0):
        return "false"
    elif act_pass==password:
        return "true"
    else:
        return "false"

