import sqlite3

# Connect to the database (will create it if not exists)
conn = sqlite3.connect('CAPSTONE-PROJECT.db')
cursor = conn.cursor()

# Create REGISTRATION table with default values
cursor.execute('''
CREATE TABLE IF NOT EXISTS REGISTRATION (
    ID INTEGER PRIMARY KEY,
    EMAIL VARCHAR(250),
    NAME VARCHAR(250),
    MASTER_PASSWORD VARCHAR(250),
    PASSWORD_HINT VARCHAR(250),
    PREFERENCES_ID INTEGER,
    EMAIL_CONFIRMED BOOLEAN DEFAULT 'N'
)
''')

# Create LOGIN table
cursor.execute('''
CREATE TABLE IF NOT EXISTS LOGIN (
    ID INTEGER PRIMARY KEY,
    EMAIL VARCHAR(250),
    LOGIN_ATTEMPTS INTEGER CHECK (LOGIN_ATTEMPTS <= 3) DEFAULT 0
)
''')

# Create ITEM table
cursor.execute('''
CREATE TABLE IF NOT EXISTS ITEM (
    ID INTEGER PRIMARY KEY,
    ITEM_TYPE_ID INTEGER,
    NAME VARCHAR(250),
    FOLDER_ID INTEGER,
    USERNAME VARCHAR(250),
    PASSWORD VARCHAR(250),
    URI VARCHAR(250),
    NOTES VARCHAR(250),
    CUSTOM_FIELD_NAME VARCHAR(255),
    CUSTOM_FIELD_TYPE INTEGER,
    CUSTOM_FIELD_VALUE VARCHAR(250)
)
''')

# Create ITEM_TYPE table with default values if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS ITEM_TYPE (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    ITEM_TYPE VARCHAR(250) 
)
''')

# Check if the ITEM_TYPE table is empty
cursor.execute("SELECT COUNT(*) FROM ITEM_TYPE")
count = cursor.fetchone()[0]

# Insert default values into the ITEM_TYPE table only if it's empty
if count == 0:
    default_types = ['login', 'Card', 'Identity', 'SecureNote']
    for item_type in default_types:
        cursor.execute("INSERT INTO ITEM_TYPE (ITEM_TYPE) VALUES (?)", (item_type,))

# Create FOLDER table
cursor.execute('''
CREATE TABLE IF NOT EXISTS FOLDER (
    ID INTEGER PRIMARY KEY,
    FOLDER_NAME VARCHAR(250)
)
''')

# Create DANGER_ZONE table
cursor.execute('''
CREATE TABLE IF NOT EXISTS DANGER_ZONE (
    ID INTEGER PRIMARY KEY,
    DEAUTHORISED_SESSION BOOLEAN,
    PURGED BOOLEAN,
    DELETED_ACCOUNT BOOLEAN,
    TIMESTAMP DATETIME,
    OWNER VARCHAR(250)
)
''')

# Create AUDIT table
cursor.execute('''
CREATE TABLE IF NOT EXISTS AUDIT (
    ID INTEGER PRIMARY KEY,
    ENTITY_TYPE_ID VARCHAR(50),
    ENTITY_ID INTEGER,
    ACTION_TYPE VARCHAR(50),
    USER_ID INTEGER,
    TIMESTAMP DATETIME
)
''')

# Create PREFERENCES table
cursor.execute('''
CREATE TABLE IF NOT EXISTS PREFERENCES (
    ID INTEGER PRIMARY KEY,
    VAULT_TIMEOUT TIME,
    THEME_ID INTEGER,
    LANGUAGE_ID INTEGER
)
''')

# Create AUDIT_ITEM_TYPE table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS AUDIT_ITEM_TYPE (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    TYPE VARCHAR(250)
)
''')

# Check if the AUDIT_ITEM_TYPE table is empty
cursor.execute("SELECT COUNT(*) FROM AUDIT_ITEM_TYPE")
count = cursor.fetchone()[0]

# Insert default values into the AUDIT_ITEM_TYPE table only if it's empty
if count == 0:
    default_types = ['REGISTRATION', 'LOGIN', 'VAULT', 'VAULT_ITEM', 'CHANGED_PASSWORD']
    for item_type in default_types:
        cursor.execute("INSERT INTO AUDIT_ITEM_TYPE (TYPE) VALUES (?)", (item_type,))



# Create VAULT_THEME table with default values
cursor.execute('''
CREATE TABLE IF NOT EXISTS VAULT_THEME (
    ID INTEGER PRIMARY KEY,
    THEME VARCHAR(250) DEFAULT 'DARK, STANDARD'
)
''')

# Check if the VAULT_THEME table is empty
cursor.execute("SELECT COUNT(*) FROM VAULT_THEME")
count = cursor.fetchone()[0]

# Insert default values into the VAULT_THEME table only if it's empty
if count == 0:
    default_themes = ['Dark', 'Standard']
    for theme in default_themes:
        cursor.execute("INSERT INTO VAULT_THEME (THEME) VALUES (?)", (theme,))


# Create LANGUAGES table with default values
cursor.execute('''
CREATE TABLE IF NOT EXISTS LANGUAGES (
    ID INTEGER PRIMARY KEY,
    LANGUAGE VARCHAR(250) 
)
''')
# Check if the LANGUAGES table is empty
cursor.execute("SELECT COUNT(*) FROM LANGUAGES")
count = cursor.fetchone()[0]

# Insert default values into the LANGUAGES table only if it's empty
if count == 0:
    default_languages = ['English', 'Spanish', 'French', 'Italian', 'Irish']
    for language in default_languages:
        cursor.execute("INSERT INTO LANGUAGES (LANGUAGE) VALUES (?)", (language,))
# Commit changes and close connection
conn.commit()
conn.close()
