import pymongo
import sys
import os
parent_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(parent_dir)
import components

# TODO: Create a new DB to store quiz answers
# TODO: Integrate with the components.py file. 
# TODO: A function to generate the all students performance. 
# Function to establish connection to MongoDB
def connection():
    client = pymongo.MongoClient("mongodb+srv://GPTadmin:xinformatics@cluster0.d1gdjlb.mongodb.net/test")
    mydb = client["GPT-Pedagogy(1)"]
    collection = mydb["UserInfo"]
    return collection

# Function to return all the document within the database => pass in database schema
def query_documents(collection):
    return collection.find()


# Function to check whether a user already exists => Using rcsid to check whether the user exist
# Parameter is database schema collection
# Return: False => Not Exist; True => Exist
def valida_user(collection, rcsid):
    validate = False
    query = {'RCSid': rcsid}
    data = collection.find_one(query)
    if data:
        print("The user already exists in the collection")
        validate = True
    else:
        print("The user does not exist in the collection")
    return validate


# Insert a new user into the database 
def insert_user(collection, rcsid, name):
    if valida_user(collection, rcsid):
        return False
    data = {
        'RCSid': rcsid,
        'Name': name,
        'Chatlog': {
        
        },
        'Performance': {
        
        }
    }
    result = collection.insert_one(data)
    print("User inserted with ID:", result.inserted_id)



# Function to update the chatlog history => conversation history. 
# Parameter are
    # Collection => database schema
    # rcsid => user crendentials; need to use the specific rcsid to update the specific chatlog 
    # title => title for the conversation
    # data => chatlog data; need to be in list format ==> example_chatlog_data = ['User: xxxxxxxxx1-231-1', 'Bot: xxxxxxxxx1-231-2', 'User: xxxxxxxxx1-231-3', 'Bot: xxxxxxxxx1-231-4']
def update_chatlog(collection, rcsid, title, data):
    # Example dictionary outline for the 'Chatlog' 
    # print(document['Chatlog']['Homework help on Chapter 1'])
    query = {'RCSid': rcsid}
    document = collection.find_one(query)
   
    if document:
        chatlog = document['Chatlog']
        if title in chatlog:
            chatlog[title].extend(data)
        else:

            chatlog[title] = data
        newvalues = {"$set": {'Chatlog': chatlog}}
        collection.update_one(query, newvalues)
    else:
        raise ValueError("Document not found for RCSid: {}".format(rcsid))


# Same idea as update_chatlog
# outcome => dictionary --> see the example performance outcome example
def update_performance(collection, rcsid, topic, outcome):
    query = {'RCSid': rcsid}
    document = collection.find_one(query)
    print(document['Performance'])

    if document:
        performance = document['Performance']
        if topic in performance:
            existing_outcome = performance[topic]['Outcome']
            if existing_outcome != outcome:
                performance[topic] = {"Topic": topic, "Outcome": outcome}
        else:
            performance[topic] = {"Topic": topic, "Outcome": outcome}

        collection.update_one(query, {"$set": {'Performance': performance}})
    else:
        raise ValueError("Document not found for RCSid: {}".format(rcsid))

        
    
'''Load chatlog and update the database'''
def load_chatlog_from_file(rcsid,title, filename):
    chatlog_data = components.load_from_file(filename)
    collection = connection()
    update_chatlog(collection, rcsid, title, chatlog_data)





if __name__ == '__main__':
    collection = connection()
    data = query_documents(collection)
    # insert_user(collection,\"liy123", "Sam")
    
    '''
    example_chatlog_data = [ 
                                {
                                    "role": "user",
                                    "content": "Hello, can you give me some hint about chapter 2 lecture? x    xxx xxxxxxxxxxxxx"
                                },
                                {
                                    "role": "system",
                                    "content": "Sure, here are some important note you can take form Chapter 2: xxxxx."
                                },
                                {
                                    "role": "user",
                                    "content": "Thank you so much"
                                },
                                {
                                    "role": "system",
                                    "content": "You're welcome"
                                }
                            ]
    '''
    
    '''
    example_performance_outcome = {
        "Question 1": "Correct",
        "Question 2": "Incorrect",
        "Question 3": "Correct",
        "Question 4": "Incorrect",
        "Question 5": "Correct",
        "Question 6": "Incorrect"
    }
    '''
    
    # update_performance(collection, 'liyu123', 'Unit test', example_performance_outcome)
    # update_chatlog(collection, 'liyu123', "Pop Quiz", example_chatlog_data)
    for document in data:
        print(document, "\n")