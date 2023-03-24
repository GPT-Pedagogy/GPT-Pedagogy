# TODO: going to play in MongoDB.

# TODO: Query function
# TODO: Update function
# TODO: create new user -> add into dbs 
# TODO: upload the performance to DBS

# mongodb+srv://GPTadmin:xinformatics@localhost/?authMechanism=SCRAM-SHA-1
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


myquery = { "RCSid": "liyu123" }



if __name__ == '__main__':
    dbs = connection()
    mydoc = query_documents(dbs)
    for x in mydoc:
        print(x)