#phase2
import pymongo  
from pymongo import MongoClient
import json
import re
from datetime import datetime
from tabulate import tabulate

default_license = 'CC BY-SA 2.5'
question_post_id = '1'
answer_post_id = '2'
database = '291db'
db_291 = None
user_id = "anon"
vote = '2'

#connect to database and server
def connect():
    global database
    global db_291

    port = input("Enter Port number:")
    if int(port)>= 65535 or int(port)<= 0:
        print("Invalid Port! Please re-enter")
        connect()
    else:
        connection = 'mongodb://localhost:' + port
        client = pymongo.MongoClient(connection)

    dblist= client.list_database_names()

    db_291 = client[database]

		
                    
def welcomePage():
    print('Welcome to Stack Underflow. Select what you would like to do')
    user_report_prompt = input('Would you like to provide user id to print a report? (y or n) ')
    
    if user_report_prompt.lower() == 'y':
        userReport()
    elif user_report_prompt.lower() == 'n':
        mainMenu()
    else:
        print('incorrect input.')
        welcomePage()


def mainMenu():
    selection = input('\n 1) Post a question \n 2) Search Post \n 0) Go back \n ')

    #edit range when adding more functionality
        
    if selection == '0': 
        welcomePage()
    elif selection == '1':
        postQuestion()
    elif selection == '2':
        searchQuestions()
    else: 
        print('Not a valid selection')
        mainMenu()

def userReport():
    global db_291
    global user_id
    while True:
        try:
          user_id = input('enter user id to print report: ')
          user_id = int(user_id)
          break
        except ValueError:
          print('This is not a valid entry for integer!')
          userReport()
    
    print('User Report')
    
    qs = []
    for x in db_291.Posts.find({"OwnerUserId": str(user_id), "PostTypeId": '1'}, {"_id": 1, "Id": 1}):
        qs.append(x["Id"]) 
    totalq = len(qs)
    # number of qs posted

    scoreq = 0
    array_q = []
    for x in db_291.Posts.find({"OwnerUserId": str(user_id), "PostTypeId": '1'},{ "Score": 1}):
        scoreq += x["Score"]

    
    #to avoid int div 0 error
    if totalq != 0:
        avgq = float(scoreq/totalq)
        avgq = round(avgq, 1)
    else:
        avgq = 0

    #avg score for user's posts

    a = []
    for x in db_291.Posts.find({"OwnerUserId": str(user_id), "PostTypeId": '2'}, {"_id": 1, "Id": 1}):
        a.append(x["Id"]) 
    totala = len(a)

    #number of answers

    scorea = 0
    array_a = []
    for x in db_291.Posts.find({"OwnerUserId": str(user_id), "PostTypeId": '2'},{ "Score": 1}):
        scorea += int(x["Score"])
        
    
    #to avoid int div 0 error
    if totala != 0:
        avga = int(scorea/totala)
        avga = round(avga, 1)
    else:
        avga = 0

    totalscore = scoreq + scorea

    
    #print in a table
    table = [['# of questions',str(totalq)],['Average Score of Questions',str(avgq)],['# of Answers', str(totala)], ['Average Score of Answers', str(avga)], ['Total score for User', str(totalscore)]]
    headers = ['Criteria', 'Value']
    print(tabulate(table, headers, tablefmt="grid"))


    mainMenu()

def postQuestion():
    global default_license
    global question_post_id
    global user_id  
    #note: ID is automatically assigned by mongodb (i think?)

    question_post = {}

    question_post["PostTypeId"] = question_post_id
    datestamp = datetime.now()
    #change later
    question_post["CreationDate"] = str(datestamp)
    question_post["ContentLicense"] = 0
    question_post["Score"] = 0
    question_post["ViewCount"] = 0
    question_post["AnswerCount"] = 0
    question_post["CommentCount"] = 0
    question_post["FavouriteCount"] = 0

    print('Add tags by typing tag and hitting enter. Hit enter twice to finish tags input.')
    tagString = ""

    tag = input('> ')
    if tag:
        tagString += "<" + tag + ">"
        question_post["Tags"] = tagString

    while tag:
        tag = input('> ')
        if tag:
            tagString += "<" + tag + ">"
            question_post["Tags"] = tagString


    print('Write question title:\n')
    title = input('> ')
    if title:
        question_post["Title"] = title


    print('Type your body:\n')
    body = input('> ')
    if body:
        question_post["Body"] = body


    if user_id != None:
        question_post["OwnerUserId"] = user_id


    #create 'Id'
    max = 0
    for x in db_291.Posts.find({}, {"_id": 1, "Id": 1}):

        if 'Id' in x:
            if max < int(x['Id']):
                max = int(x['Id'])

    print(max)
    pid = max +1

    question_post["Id"] = str(pid)



    '''
    max_value = db_291.Posts.find_one(sort = [("Id", -1)])
    print('max_value: ', max_value)
    assign_id = max_value + 1
    print(assign_id)
    '''
    
    '''
    insert into database...
    '''
    posts_collection = db_291['Posts']
    ret = posts_collection.insert_one(question_post)
    print('ID of question submitted: ', ret.inserted_id)

    mainMenu()

def searchQuestions():
   
    global db_291

    clean = re.compile('<.*?>')

    term_keywords = []
    short_keywords = []
    print('Search for questions (enter keyword. Or two. Or how many you like)')
    keywords = input('> ')
    short_keyword_regex = ""
    contains_short = False
    keywords_list = re.split('[^0-9a-zA-Z]', keywords)
    for i in keywords_list:
        if len(i) < 3 and i != '':
            contains_short = True
            short_keyword_regex += "(?=.*" + i.lower() + ")"
        if len(i) >= 3 and i != '':
            term_keywords.append(i.lower())

    print('Keywords:', keywords_list)
    print('term keywords: ', term_keywords)
    print('Short Regex:', short_keyword_regex)

    i = 0
    ranOnce = False
    for post in db_291.Posts.find({"PostTypeId": "1", "terms": {"$all" : term_keywords}},{"_id": 1, "Id": 1, "Body": 1, "Title": 1, "Tags": 1}):
        
        if (i%5) == 0 and ranOnce:
            wait = True
            while wait:
                print('0) Return to Menu\n1) Show next 5 search results\n2) Choose a Post\n')
                check = input('>')
                if check == '0':
                    mainMenu()
                elif check == '1':
                    wait = False
                elif check == '2':
                    chosenId = input("Post Id: ")
                    for x in db_291.Posts.find({"PostTypeId": "1", "Id": chosenId}, {}):
                        QuestionMenu(chosenId)
                        break
                    else:
                        print('No Post with that Id found.')
                else:
                    print('Invalid Input.')
                            

        i += 1
        ranOnce = True
        if post['Id'] != None:
            print('------------',str(i) + ')')
            print('\n')
            print("Id: " + post['Id'])
            print('\n')
            if 'Title' in post:
                title = re.sub(clean, '', post['Title'])
                print('Title: ' + title)
            if 'Body' in post:
                body = re.sub(clean, '', post['Body'])
                print("Body: " + body)
            db_291["Posts"].update_one( {"Id" : post['Id']} ,{"$inc" : {"ViewCount": 1}} , True, False)
        
        
        

    if contains_short:
        for post in db_291.Posts.find({"PostTypeId": "1", "$or": [{"Title": {"$regex" : short_keyword_regex, '$options' : 'i'}}, {"Body": {"$regex" : short_keyword_regex, '$options' : 'i'}}, {"Tags": {"$regex" : short_keyword_regex,'$options' : 'i'}}]},{"_id": 1, "Id": 1, "Body": 1, "Title": 1, "Tags": 1}):
            
            if (i%5) == 0 and ranOnce:
                wait = True
                while wait:
                    print('0) Return to Menu\n1) Show next 5 search results\n2) Choose a Post\n')
                    check = input('>')
                    if check == '0':
                        mainMenu()
                    elif check == '1':
                        wait = False
                    elif check == '2':
                        chosenId = input("Post Id: ")
                        for x in db_291.Posts.find({"PostTypeId": "1", "Id": chosenId}, {}):
                            QuestionMenu(chosenId)
                            break
                        else:
                            print('No Post with that Id found.')
                    else:
                        print('Invalid Input.')
                i += 1
                ranOnce = True
                if post['Id'] != None:
                    print('------------',str(i) + ')')
                    print('\n')
                    print("Id: " + post['Id'])
                    print('\n')
                    if 'Title' in post:
                        title = re.sub(clean, '', post['Title'])
                        print('Title: ' + title)
                    if 'Body' in post:
                        body = re.sub(clean, '', post['Body'])
                        print("Body: " + body)
                    db_291["Posts"].update_one( {"Id" : post['Id']} ,{"$inc" : {"ViewCount": 1}} , True, False)
            
    wait = True
    while wait:
        print('0) Return to Menu\n1) Choose a Post\n')
        check = input('>')
        if check == '0':
            wait = False
            mainMenu()
        elif check == '1':
            chosenId = input("Post Id: ")
            for x in db_291.Posts.find({"PostTypeId": "1", "Id": chosenId}, {}):
                QuestionMenu(chosenId)
                break
            else:
                print('No Post with that Id found.')
        else:
            print('Invalid Input.')



    #When searching, Questions should show up, with title, creation date, score, and answer count.
    #Upon selecting a question, more fields should show up
def QuestionMenu(qid):
    print('What would you like to do with question ' + str(qid))
    selection = input('0)Return to Menu\n1) Answer Question\n2) List Answers\n3)Cast a Vote\n')

    #edit range when adding more functionality
        
    if selection == '0': 
        mainMenu()
    elif selection == '1':
        AnswerQuestion(qid)
    elif selection == '2':
        ListAnswers(qid)
    elif selection == '3':
        votePost(qid)
    else:
        print('Not a valid selection')
        QuestionMenu(qid)
        
        
def AnswerQuestion(qid):
    global default_license
    global answer_post_id
    global user_id

    answer_post = {}

    answer_post["PostTypeId"] = answer_post_id 
    datestamp = datetime.now() 
    answer_post["CreationDate"] = str(datestamp)
    answer_post["Score"] = 0 
    answer_post["CommentCount"] = 0 
    answer_post["ParentId"] = qid 

    #provide title
    print('Provide a title for this answer and bless your soul! \n')
    title = input('> ')

    #if title is actually provided
    if title != '':
        answer_post["Title"] = title

    print('\n')

    #provide answer
    print('Provide your detailed answer here. \n')
    body = input('> ')

    #if body is actually provided
    if body != '':
        answer_post["Body"] = body
    print('\n')

    if user_id != None:
        answer_post["OwnerUserId"] = user_id

    max = 0
    for x in db_291.Posts.find({}, {"_id": 1, "Id": 1}):

        if 'Id' in x:
            if max < int(x['Id']):
                max = int(x['Id'])

    pid = max +1

    answer_post["Id"] = str(pid)


    posts_collection = db_291['Posts']
    ret = posts_collection.insert_one(answer_post)
    print('ID of question submitted: ', ret.inserted_id)

    QuestionMenu(qid)

def votePost(pid):
    global user_id
    global vote
    global db_291

    avote= {}

    if user_id != None:
        avote["UserId"] = user_id
        for x in  db_291.Votes.find({"UserId": user_id, "PostId": pid}, {}):
            print('You have already voted on this post.')
            mainMenu()
        
            

    user_vote = input('Place a vote on the post y/n?\n')
    if user_vote == 'y':

        avote["VoteTypeId"] = vote 
        datestamp = datetime.now() 
        avote["CreationDate"] = str(datestamp)

        max = 0
        for x in db_291.Votes.find({}, {"_id": 1, "Id": 1}):
            if 'Id' in x:
                if max < int(x['Id']):
                    max = int(x['Id'])
        vid = max +1
        avote["Id"] = vid
        avote ["PostId"] = pid
        votescol = db_291['Votes']
        postscol = db_291['Posts']
        
        db_291["Posts"].update_one( {"Id" : pid} ,{"$inc" : {"Score": 1}} , True, False)
        ret = votescol.insert_one(avote)
        print('ID of question submitted: ', ret.inserted_id)
        print('Vote Casted')

    elif user_vote == 'n':
        QuestionMenu(pid)
    else:
        print("Incorrect input!")
        votePost(pid)

    QuestionMenu(pid)

def ListAnswers(qid):
    global db_291

    print("Listing answers for Post: " + qid)
    
    i = 0
    ranOnce = False
    for x in db_291.Posts.find({"PostTypeId": "2", "ParentId": qid}, {"_id": 1, "Id": 1, "Body": 1, "Title": 1, "Tags": 1}):
        
        if (i%5) == 0 and ranOnce:
            wait = True
            while wait:
                print('0) Return to Menu\n1) Show next 5 answers\n2)Vote on Answer')
                check = input('>')
                if check == '0':
                    mainMenu()
                elif check == '1':
                    wait = False
                elif check == '2':
                    id = input('Answer PostId: ')
                    for x in db_291.Posts.find({"PostId":id},{}):
                        for x in db_291.Votes.find({"UserId": user_id, "PostId": id}, {}):
                            print('You have already voted on this post.')
                            break
                        else:
                            votePost(id)
                    else:
                        print('No Post found with that Id.')
                else: 
                    print('Invalid Input.')
        i += 1
        ranOnce = True
        if x['Id'] != None:
            print(str(i) + ')')
            print("Id: " + x['Id'])
            if 'Title' in x:
                print("Title: " + x['Title'])
            if 'Body' in x:
                print("Body: " + x['Body'])
    
    wait = True
    while wait:
        print('0) Return to Menu\n1) Choose an Answer Post\n')
        check = input('>')
        if check == '0':
            wait = False
            mainMenu()
        elif check == '1':
            id = input('Answer PostId: ')
            for x in db_291.Posts.find({"PostId":id},{}):
                for x in db_291.Votes.find({"UserId": user_id, "PostId": id}, {}):
                    print('You have already voted on this post.')
                    break
                else:
                    votePost(id)
            else:
                print('No Post found with that Id.')
        else: 
            print('Invalid Input.')
    


def exitPage():
    print('Goodbye!')
    exit()

def main():
    connect()
    welcomePage()

if __name__ == "__main__":
    main()