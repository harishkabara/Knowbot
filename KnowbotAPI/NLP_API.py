
from flask import Flask,jsonify,request
from NLP import nlp as func
from NLP import feedback as feedbackfunc
from NLP import userloginsert as userinsertfunc
from NLP import likedislikecount as countfunc
from NLP import wikiapicall as wikifunc
from NLP import investopediacall as linkfunc
from Admin import admintask as adminfunc, user_info
from Admin import downloadtask as download
from Admin import  searchquestion as searchquery
from Admin import getanswers as answers
from Admin import delete_question
from Admin import delete_users
from Admin import add_user
from Admin import check_admin
from Admin import validate_superadmin
from Admin import downloadfeedback
from Admin import downloadunanswered
from Admin import feedbackcount
from Admin import unansweredcount
import json
app = Flask(__name__)
@app.route('/',methods=['GET'])
def hello_world():

    return jsonify({"object":"hello world"})

@app.route('/user/answer',methods=['PUT'])
def answer():
    dict = request.get_json()
    ques= dict.get("question")
    ans = func(ques)
    print(ans.get("answer"))
    if ans.get("answer") == None:
        if ans.get("spell")== "Correct":
            answ= {"answer":"ERROR","type":ans.get("question"),"count":ans.get("count"),"identifier":"spellcorrectnotmatch","question":ans.get("correctedquestion")}
            print(answ)
        else:
            answ = {"answer": "ERROR", "type": ans.get("question"), "count": ans.get("count"), "identifier":"spellincorrectnotmatch",
                    "question": ans.get("correctedquestion")}
    else:
        for ele in ans.get("answer"):
            ansq = ele
        countarray=countfunc(ansq)
        likecount= str(countarray.get("like"))
        dislikecount=str(countarray.get("dislike"))
        if ans.get("spell") == "Correct":
           answ= {"answer":ansq,"type":"ERROR","likecount":likecount,"dislikecount":dislikecount,"identifier":"spellcorrectmatch","question":ans.get("correctedquestion")}
        else:
           answ = {"answer": ansq, "type": "ERROR", "likecount": likecount, "dislikecount": dislikecount,
                   "identifier":"spellincorrectmatch", "question": ans.get("correctedquestion")}
    return jsonify(answ)

@app.route('/user/feedback', methods=['PUT'])
def feedback():
    feedjson= request.get_json()
    print(feedjson)
    answer= feedjson.get("answer")
    score = feedjson.get("score")
    userid=feedjson.get("userid")
    score=int(score)
    feedbackfunc(answer,score,userid)
    return  jsonify({"work":"done"})
@app.route('/user/dbload', methods=['GET'])
def dbload():
    investdb=[]
    client = MongoClient('localhost', 27017)
    db = client['chatbot']
    collection = db['investtoken']
    counter=0
    result=collection.find()
    response1 = ""
    urllist=[]
    for res in result:

            urllist.append(res.get("URL"))
            urllist.append(res.get("TOKEN"))
            print(res.get("TOKEN"))
            counter=counter+1

    return jsonify({"db":urllist})

@app.route('/user/userlog', methods=['PUT'])
def userlog():
    userlogjson= request.get_json()
    question= userlogjson.get("question")
    username = userlogjson.get("username")
    userinsertfunc(question,username)
    return  jsonify({"work":"done"})
@app.route('/user/links', methods=['PUT'])
def invest():
    userlogjson= request.get_json()
    question= userlogjson.get("question")
    linkset=linkfunc(question)
    return  jsonify({"links":linkset.get("links")})
@app.route('/user/wiki', methods=['PUT'])
def userwiki():
    userwikijson= request.get_json()
    question= userwikijson.get("question")
    result= wikifunc(question)
    counter=0
    type1=[]
    type2=[]
    type3=[]
    for it in result:
        if counter<3 and counter>=0:
         type1.append(it)
        if counter < 6 and counter>=3:
         type2.append(it)
        if counter<9 and counter>=6:
         type3.append(it)
        counter=counter+1
    return  jsonify({"type1":type1,"type2":type2,"type3":type3})

@app.route('/admin/upload',methods=['PUT'])
def answer1():
    dict = request.get_json()
    response=adminfunc(dict)
    print(response)
    #answ= "{\"message\":"+response+"\"}"
    answ={}
    answ['message'] = response
    #answ={"message":response}
    return jsonify(answ)

@app.route('/admin/download/',methods=['GET'])
def answer2():

    response=download()
    response1=""
    for res in response:
        print(res)
        #dict = res.get_json()
        ques = res.get("question")
        ans=res.get("answer")
        score=str(res.get("customer_score"))

        response1=response1+"||"+ques+"|"+ans+"|"+score
       # for k, v in res.items():  # d.items() in Python 3+
            #response1.setdefault(k, []).append(v)
    print(response1)
    answ = {}
    answ['message'] = response1
    return jsonify(answ)

@app.route('/admin/download-unsatisfied-question/',methods=['GET'])
def download_feedback():

    response=downloadfeedback()
    response1=""
    for res in response:
        print(res)
        #dict = res.get_json()
        ques = res.get("question")
        answer=res.get("answer")

        response1=response1+"####"+ques+"|"+answer
       # for k, v in res.items():  # d.items() in Python 3+
            #response1.setdefault(k, []).append(v)
    print(response1)
    answ = {}
    answ['message'] = response1
    return jsonify(answ)
@app.route('/admin/unsatisfied-question-count/',methods=['GET'])
def count_feedback():

    response=feedbackcount()
    answ = {}
    answ['message'] = str(response)
    return jsonify(answ)
@app.route('/admin/download-unanswered-question/',methods=['GET'])
def download_unanswered():

    response=downloadunanswered()
    response1=""
    for res in response:
        print(res)
        #dict = res.get_json()
        ques = res.get("question")
        id=res.get("user_id")

        response1=response1+","+ques+"|"+id
       # for k, v in res.items():  # d.items() in Python 3+
            #response1.setdefault(k, []).append(v)
    print(response1)
    answ = {}
    answ['message'] = response1
    return jsonify(answ)
@app.route('/admin/unanswered-question-count',methods=['GET'])
def count_unanswered():
    response=unansweredcount()
    answ = {}
    answ['message'] = str(response)
    return jsonify(answ)
@app.route('/admin/search', methods=['PUT'])
def search():
    dict = request.get_json()
    response = searchquery(dict)
    response1 = response.split("|,")
    response2=response1[1]
    print(response2)
    answ = {}
    answ['message'] = response2
    return jsonify(answ)

@app.route('/admin/get-answer', methods=['PUT'])
def getanswer():
    dict = request.get_json()
    response = answers(dict)
    for res in response:
        ans=res.get("answer")
    answ = {}
    answ['message'] = ans
    return jsonify(answ)
    #return jsonify({"object": "hello world"})
@app.route('/admin/delete-question', methods=['PUT'])
def deleteques():
    dict = request.get_json()
    response = delete_question(dict)
    answ = {}
    answ['message'] = response
    return jsonify(answ)
@app.route('/admin/delete-user', methods=['PUT'])
def deleteuser():
    dict = request.get_json()
    response = delete_users(dict)
    answ = {}
    answ['message'] = response
    return jsonify(answ)
@app.route('/admin/add-user', methods=['PUT'])
def adduser():
    dict = request.get_json()
    response = add_user(dict)
    answ = {}
    answ['message'] = response
    return jsonify(answ)
@app.route('/admin/user-management', methods=['GET'])
def getuser():
   #dict = request.get_json()
    response = user_info()
    response1 = ""
    for res in response:
        id=res.get("admin_id")
        name=res.get("name")
        response1=response1+","+id+"|"+name
    answ = {}
    answ['message'] = response1
    return jsonify(answ)
@app.route('/admin/check-admin', methods=['PUT'])
def checkadmin():
    dict = request.get_json()
    response = check_admin(dict)
    answ = {}
    answ['message'] = response
    return jsonify(answ)
@app.route('/admin/loginadmin', methods=['PUT'])
def validateadmin():
    dict = request.get_json()
    response = validate_superadmin(dict)
    answ = {}
    answ['message'] = response
    return jsonify(answ)
if __name__ == '__main__':

#change the IP address of the host machine
    app.run(host="10.245.118.10",port=5000,debug=True,threaded= True)
    #app.run(debug=True, threaded=True)
