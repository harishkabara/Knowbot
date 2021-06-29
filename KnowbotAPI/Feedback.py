
from pymongo import MongoClient


client = MongoClient('localhost', 27017)
db = client['chatbot']
collection = db['NLPdb']
collection1=db['user_questions']

def feedback(ans,score):
    resultset=collection.find({"answer":ans})
    if resultset.count()>0:
        for res in resultset:
            customer_score=res.get("customer_score")
        if (not res.get('customer_score'))==0:
            score1 = customer_score + int(score)
            if (score1 <= 5):
                collection.delete_one({"answer":ans})
                ques=res.get('question')
                collection1.insert({"question":ques})
            else:
                collection.update({"answer": ans}, {"$set": {"customer_score": score1}})


        else:
            score1 = int(score)
            collection.update({"answer": ans}, {"$set": {"customer_score": score1}})
        message="successfully updated score for answer-"+ans
        return message
    else:
        message="answer does not exist"
        return message

