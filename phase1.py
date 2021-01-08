import pymongo  
from pymongo import MongoClient
import json
import re
from datetime import datetime

start = None
db_291 = None
postscol = None

def connect():
    global start
    global db_291
    global postscol

    port = input("Enter Port number:")
    if int(port)>= 65535 or int(port)<= 0:
        print("Invalid Port! Please re-enter")
        connect()
    else:
        start = datetime.now()
        connection = 'mongodb://localhost:' + port
        client = pymongo.MongoClient(connection)


    db_291 = client["291db"]
    
    
    collec_list = db_291.list_collection_names()

    if "Posts" in collec_list:
        db_291["Posts"].drop()
    
    elif "Votes" in collec_list:
        db_291["Votes"].drop()
    
    elif "Tags" in collec_list:
        db_291["Tags"].drop()
    

    postscol = db_291["Posts"]
    tagscol = db_291["Tags"]
    votescol = db_291["Votes"]
    mydict = { "name": "John", "address": "Highway 37" }

    
    with open("Tags.json") as f:
        file_data = json.load(f)
    tagscol.insert_many(file_data['tags']['row'])
    
    
    with open("Posts.json") as f:
        file_data = json.load(f)
    postscol.insert_many(file_data['posts']['row'])
    
    
    with open("Votes.json") as f:
        file_data = json.load(f)
    votescol.insert_many(file_data['votes']['row'])
    

    collec_list = db_291.list_collection_names()
    print('Collections created:', collec_list)

    return

def BuildTerms():
    global start
    global db_291
    global postscol

    i = 1
    for x in postscol.find({},{"_id": 1, "Body": 1, "Title": 1, "Tags": 1}):

        terms = []

        if 'Title' in x:

            tempTerms = re.split('[^0-9a-zA-Z]', x['Title'].lower())

            for term in tempTerms:
                if term not in terms and len(term) >= 3:
                    terms.append(term)

        if 'Body' in x:

            tempTerms = re.split('[^0-9a-zA-Z]', x['Body'].lower())

            for term in tempTerms:
                if term not in terms and len(term) >= 3:
                    terms.append(term)
        
        if 'Tags' in x:

            tempTerms = re.split('[^0-9a-zA-Z]', x['Tags'].lower())

            for term in tempTerms:
                if term not in terms and len(term) >= 3:
                    terms.append(term)

        
        db_291["Posts"].update( {"_id" :x['_id']} ,{"$set" : {"terms": terms}} , True, True)
        
        i += 1
    
    print("# of Posts terms built for: " + str(i))
    print('Indexing...')
    db_291["Posts"].create_index([("terms", 1)])
    print("indexed!")
    print('Time for execution: ', datetime.now() - start)

    return

 

def main():

    connect()
    BuildTerms()


if __name__ == "__main__":
    main()