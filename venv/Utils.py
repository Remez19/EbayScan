import pyodbc


def connectToDB(serverName, dbName):
    """
       : Establish a connection to a Data - Base
       :param serverName: The name of the server.
       :param dbName: The name of the Data - Base.
       :return session.get: The session.
       """
    try:
        # Establish SQL server connection to insert data
        # Define our connection string
        connect = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server}; \
                                                     SERVER=' + serverName + '; \
                                                     DATABASE=' + dbName + ';\
                                                     Trusted_Connection=yes;')
        # Create the connection cursor
        return connect.cursor()
    except Exception:
        print("Cannot connect to DB Failuer")
        exit(1)


def insertToDB(dataBaseCon, data, insertQuery):
    """
          : Handle insert query's to Data - Base.
          :param dataBaseCon: The connection to Data - Base.
          :param data: The data to insert.
          :param insertQuery: The insert query to preform.
          """
    try:
        dataBaseCon.execute(insertQuery, data)
        dataBaseCon.commit()
    except Exception as e:
        print(insertQuery + "  -> Fail")
        print(e)


def deleteFromDB(dataBaseCon, deleteQuery):
    """
          : Handle delete query's to Data - Base.
          :param dataBaseCon: The connection to Data - Base.
          :param deleteQuery: The delete query to preform.
          """
    try:
        dataBaseCon.execute(deleteQuery)
        dataBaseCon.commit()
    except Exception as e:
        print(deleteQuery + "  -> Fail")
        print(e)


def selectFromDB(dataBaseCon, selectQuery, queue=None):
    """

          : Handle select query's to Data - Base.
          :param queue: queue to insert data (for threads)
          :param dataBaseCon: The connection to Data - Base.
          :param selectQuery: The select query to preform.
          :return Data: A list of the data.
          """
    try:
        if queue is not None:
            dataBaseCon.execute(selectQuery)
            for row in dataBaseCon:
                queue.put(row)
        else:
            data = []
            dataBaseCon.execute(selectQuery)
            for row in dataBaseCon:
                data.append(row)
            return data
    except Exception as e:
        print(selectQuery + '  -> Fail')