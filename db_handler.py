from connect_db import Db_connection
import os
from dotenv import load_dotenv

load_dotenv()
def create_job(db_table_name,data,db_name):

    """
     Args:
        table_name: <str>
        data: <dict>
        db_name: <str>

    """
   

    try:
        client = Db_connection()
        db = client[db_name]
        col = db[db_table_name]
        
        result=col.insert_one(data)
        
     
        return result

    except Exception as e:
        
        return False


def update_db(table_name, condition, to_update, db_name,upsert=True):
    """
    Adds/ modifis a document in mongoDB.

    Args:
        table_name: <str>
        condition: <dict>
        to_update: <dict>
        db_name: <str>

    Returns:
        bool: True if function has executed properly, false otherwise

    Raises:
        Exception with dedicated error code

    """

    try:
       
        client = Db_connection()
        db = client[db_name]
        col = db[table_name]
        col.update_one(condition, {"$set" : to_update}, upsert=upsert)
        
       
        return True


    except Exception as e:
      
        print("Error updating db",e)
        return False
    
def get_job(table_name, condition, db_name):
    """
    Gets a document from the database based on the provided condition.

    Args:
        table_name (str): The name of the collection/table in the database.
        condition (dict): The condition to filter the documents.
        db_name (str): The name of the database.

    Returns:
        dict: The document if found, None if no document matches the condition.
        bool: False if an error occurs during the operation.

    Raises:
        Exception: Propagates exceptions if there is an error with a dedicated error message.
    """
    try:
        # Establish a connection to the database
        client = Db_connection()
        db = client[db_name]
        col = db[table_name]

        # Fetch the document based on the condition
        document = col.find_one(condition)

        return document

    except Exception as e:
        # Log or handle the exception as needed
        print(f"An error occurred: {e}")
        return False
