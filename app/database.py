import sqlite3
from sqlite3 import Error

db_file = "CAPSTONE-PROJECT.db"

def connect(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
        return None

def create_connection(db_file):
    """ create a database connection to a SQLite database """

    try:
        conn = connect(db_file)
        if conn is not None:
            cursor = conn.cursor()

            cursor.execute('''CREATE TABLE IF NOT EXISTS REGISTRATION (
                      ID INTEGER PRIMARY KEY,
                      USER_ID INTEGER UNIQUE,
                      EMAIL VARCHAR(250) UNIQUE,
                      NAME VARCHAR(250),
                      MASTER_PASSWORD VARCHAR(250),
                      PASSWORD_HASH VARCHAR(250),
                      PASSWORD_HINT VARCHAR(250),
                      PREFERENCES_ID INTEGER,
                      EMAIL_CONFIRMED BOOLEAN DEFAULT 'N',
                      /* FOREIGN KEY (USER_ID) REFERENCES LOGIN(ID) ON DELETE CASCADE, */
                      FOREIGN KEY (PREFERENCES_ID) REFERENCES PREFERENCES(ID) ON DELETE CASCADE
                  ) ''')
            # Not required password_hash moved to registration table
            """cursor.execute('''
                    CREATE TABLE IF NOT EXISTS LOGIN (
                          ID INTEGER PRIMARY KEY,
                          EMAIL VARCHAR(250) UNIQUE,
                          PASSWORD_HASH VARCHAR(250)
                      )
                      ''')"""

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS FOLDER (
                      ID INTEGER PRIMARY KEY,
                      USER_ID INTEGER,
                      FOLDER_NAME VARCHAR(250),
                      FOREIGN KEY (USER_ID) REFERENCES LOGIN(ID) ON DELETE CASCADE
                  ) ''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS ITEM (
                          ID INTEGER PRIMARY KEY,
                          USER_ID INTEGER,
                          FOLDER_ID INTEGER,
                          ITEM_TYPE_ID INTEGER,
                          NAME VARCHAR(250),
                          USERNAME VARCHAR(250),
                          PASSWORD VARCHAR(250),
                          URI VARCHAR(250),
                          NOTES VARCHAR(250),
                          CUSTOM_FIELD_NAME VARCHAR(255),
                          CUSTOM_FIELD_TYPE INTEGER,
                          CUSTOM_FIELD_VALUE VARCHAR(250),
                          FOREIGN KEY (USER_ID) REFERENCES LOGIN(ID) ON DELETE CASCADE,
                          FOREIGN KEY (FOLDER_ID) REFERENCES FOLDER(ID) ON DELETE CASCADE
                      ) ''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS ITEM_TYPE (
                          ID INTEGER PRIMARY KEY AUTOINCREMENT,
                          ITEM_TYPE VARCHAR(250) 
                      )''')

            cursor.execute(''' CREATE TABLE IF NOT EXISTS PREFERENCES (
                          ID INTEGER PRIMARY KEY,
                          USER_ID INTEGER,
                          VAULT_TIMEOUT TIME,
                          THEME_ID INTEGER,
                          LANGUAGE_ID INTEGER,
                          FOREIGN KEY (USER_ID) REFERENCES LOGIN(ID) ON DELETE CASCADE
                      )''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS AUDIT (
                          ID INTEGER PRIMARY KEY,
                          ENTITY_TYPE_ID VARCHAR(50),
                          ENTITY_ID INTEGER,
                          ACTION_TYPE VARCHAR(50),
                          USER_ID INTEGER,
                          TIMESTAMP DATETIME,
                          FOREIGN KEY (USER_ID) REFERENCES LOGIN(ID) ON DELETE CASCADE
                      )''')

    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()



def displayData():
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        data = cursor.execute('''SELECT * FROM FOLDER ''')

        print("Data in the table FOLDER: ")
        for row in data:
            print(row)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
 displayData()
   # create_connection("CAPSTONE-PROJECT.db")


