import pymongo

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



# TODO: Update function (update the chatlog, update the performance)
# TODO: upload the performance to DBS (and chatlog)




if __name__ == '__main__':
    collection = connection()
    data = query_documents(collection)
    # insert_user(collection, "liy123", "Sam")

    for document in data:
        print(document, "\n")