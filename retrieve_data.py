import sqlite3
import pandas as pd

def retrieve_data(db_name: str, query: str):
    """
    Function takes in an SQL Query as input and
    returns a pandas dataframe created from the retrieved data
    """
    # Connecting to Database
    connection = sqlite3.connect(db_name)
    # Creating database Cursor
    cur = connection.cursor()
    try:
        # Executing SQL query on the database
        res = cur.execute(query)
    except Exception as e:
        print(e)
        return None, False #Returning - No dataframe, Operation Failed
    # Comit
    connection.commit()
    # Storing retrieved data
    data = res.fetchall()
    # If query was for retrieval, return dataframe
    if res.description:
        # Retrieving Column names from res if the query was for retrieval
        columns = [desc[0] for desc in res.description]
        # Creating the dataframe
        df = pd.DataFrame(data=data, columns=columns)
        # Closing Connection
        connection.close()
        return df, True #Returning - Dataframe, Operation Success
    # Closing Connection
    connection.close()
    return None, True # Returning - No Dataframe, Operation Success