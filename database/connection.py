import pymongo


def connection():
    """Establishes a connection to mongodb

    :return: A collection of user metadata"""

    client = pymongo.MongoClient("mongodb+srv://GPTadmin:xinformatics@cluster0.d1gdjlb.mongodb.net/test")
    mydb = client["GPT-Pedagogy(1)"]
    collection = mydb["UserInfo"]
    return collection


def query_documents(collection: pymongo.collection.Collection, **kwargs):
    """Finds all documents within the database => pass in database schema

    :param collection: The MongoDB collection containing the user data
    :return: All relevant documents in the database"""

    return collection.find(**kwargs)


def validate_user(collection: pymongo.collection.Collection, rcs_id: str):
    """Checks whether a user with the given RCS id exists in the database

    :param collection: The MongoDB collection containing the user data
    :param rcs_id: The RCS id of the user to look for
    :return: ``True`` if the user exists, ``False`` otherwise"""


    query = {'RCSid': rcs_id}
    data = collection.find_one(query)
    user_exists = True if data else False

    print(f"The user {'already exists' if user_exists else 'does not exist'} in the collection")

    return user_exists


def insert_user(collection: pymongo.collection.Collection, rcs_id: str, username: str):
    """Inserts a new user into the database

    :param collection: The MongoDB collection containing the user data
    :param rcs_id: The RCS id of the user to insert
    :param username: The name of the user to add"""

    if validate_user(collection, rcs_id):
        return False

    data = {
        'RCSid': rcs_id,
        'Name': username,
        'Chatlog': {
        
        },
        'Performance': {
        
        }
    }
    result = collection.insert_one(data)
    print("User inserted with ID:", result.inserted_id)


def update_chatlog(collection: pymongo.collection.Collection, rcs_id: str, title: str, data: list[str]):
    """Updates the conversation history of the user with the given RCS id

    **Examples**

    >>> data
    >>> ['User: xxxxxxxxx1-231-1', 'Bot: xxxxxxxxx1-231-2', 'User: xxxxxxxxx1-231-3', 'Bot: xxxxxxxxx1-231-4']

    :param collection: The MongoDB collection containing the user data
    :param rcs_id: The RCS id of the user to update
    :param title: The title of the conversation
    :param data: A list of new chats to add to the chatlog
    :raise ValueError: If there is no existing document for the user with the given RCS id"""

    # Example dictionary outline for the 'Chatlog' 
    # print(document['Chatlog']['Homework help on Chapter 1'])
    query = {'RCSid': rcs_id}
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
        raise ValueError(f"Document not found for RCSid: {rcs_id}")


def update_performance(collection: pymongo.collection.Collection, rcs_id: str, topic: str, outcome: dict):
    """Updates the quiz performance history of the user with the given RCS id

    :param collection: The MongoDB collection containing the user data
    :param rcs_id: The RCS id of the user to update
    :param topic: The topic that the user was quizzed on
    :param outcome: The user's performance on the given topic
    :raise ValueError: If there is no existing document for the user with the given RCS id"""

    query = {'RCSid': rcs_id}
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
        raise ValueError("Document not found for RCSid: {}".format(rcs_id))


if __name__ == '__main__':
    mongo_collection = connection()
    data = query_documents(mongo_collection)
    # insert_user(collection, "liy123", "Sam")
    example_chatlog_data = ['User: xxxxxxxxx1-231-1', 'Bot: xxxxxxxxx1-231-2', 'User: xxxxxxxxx1-231-3', 'Bot: xxxxxxxxx1-231-4']
    example_performance_outcome = {
        "Question 1": "Correct",
        "Question 2": "Incorrect",
        "Question 3": "Correct",
        "Question 4": "Incorrect",
        "Question 5": "Correct",
        "Question 6": "Incorrect"
    }
    update_performance(mongo_collection, 'liyu123', 'Unit test', example_performance_outcome)
    # update_chatlog(collection, 'liyu123', "Pop Quiz", example_chatlog_data)
    # for document in data:
    #     print(document, "\n")