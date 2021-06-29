def nlpmongo(toklist):
    from pymongo import MongoClient
    import json
    import ast
    from itertools import combinations
    import math
    result={}
    client = MongoClient('localhost', 27017)
    db = client['KnowBot']
    collection = db['NLPdb']
    collection1 = db['token']
    wordlist = collection1.find()
    sumtotcount=0
    tokenlist = toklist
    count = tokenlist.__len__()
    combination = list(combinations(tokenlist, count))
    temptoken = ""
    answerset = []
    for com in combination:
        for test in com:
            if temptoken == "":
                temptoken = "{'token':'" + test + "'"
            else:
                temptoken = temptoken + ",'token':'" + test + "'"
    x1 = temptoken + "}"
    queryand = "{'$and':[" + x1 + "]}"
    jsonquery = ast.literal_eval(queryand)
    dbresult = collection.find(jsonquery)
    for dbr in dbresult:
        if dbr.get("token").__len__() == count:
          flag = "Y"
          for tokenarray in dbr.get("token"):
            if tokenarray not in tokenlist:
                flag = "N"
          if flag =="Y":
           answerset.append(dbr.get("answer"))
    if answerset == []:
        temptoken = ""
        for ls in tokenlist:
            if temptoken == "":
                temptoken = "{'token':'" + ls + "'"
            else:
                temptoken = temptoken + "},{'token':'" + ls + "'"

        x1 = temptoken + "}"
        x2 = "{'$or':[" + x1 + "]}"
        b = ast.literal_eval(x2)
        a = collection.find(b)
        questionlist = []
        scorelist = []
        typeque = []
        for x in a:
            arr = x.get("token")
            print(arr)
            ques = x.get("question")
            sum = 0
            count = 0
            for tok in arr:
                idf=0
                if tok in tokenlist:
                    name=collection1.find({"token":tok})
                    for n in name:
                        idf = n.get("IDFScore")
                    idf= int(idf)
                    sum = sum + idf
                    count = count + 1
            tf = count / arr.__len__()
            score = tf * sum
            questionlist.append(ques)
            scorelist.append(score)
        topthree = sorted(zip(scorelist, questionlist), reverse=True)[:3]
        for top in topthree:
            qu = top.__getitem__(1)
            typeque.append(qu)
        result = {"question":typeque}
    else:
        result = {"answer": answerset}
    return result
