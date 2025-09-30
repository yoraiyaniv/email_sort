import mysql.connector


class Database:
    
    def __init__(self, host, user, password, database):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.connection.cursor(dictionary=True)

    def execute_query(self, query, params=None):
        self.cursor.execute(query, params or ())
        self.connection.commit()
        return self.cursor

    def fetch_all(self, query, params=None):
        self.cursor.execute(query, params or ())
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.connection.close()


class UserDatabase(Database):
    _instance = None
    
    def __new__(cls, host, user, password, database):
        if cls._instance is None:
            cls.instance = super(UserDatabase, cls).__new__(cls)
            cls.instance._init_connection(host, user, password, database)
        return cls.instance

    def _init_connection(self, host, user, password, database):
        super().__init__(host, user, password, database)
    
    def create_users_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.execute_query(query)
    
    def add_user(self, username, email, password_hash):
        query = """
        INSERT INTO users (username, email, password_hash)
        VALUES (%s, %s, %s)
        """
        self.execute_query(query, (username, email, password_hash))
    
    def authenticate_user(self, username, password_hash):
        query = """
        SELECT * FROM users WHERE username = %s AND password_hash = %s
        """
        result = self.fetch_all(query, (username, password_hash))
        return result[0] if result else None
    
    def check_username__or_email_exists(self, username, email):
        query = """
        SELECT * FROM users WHERE username = %s OR email = %s
        """
        result = self.fetch_all(query, (username, email))
        return len(result) > 0
    
class LabelsDatabase(Database):
    _instance = None
    
    def __new__(cls, host, user, password, database):
        if cls._instance is None:
            cls.instance = super(LabelsDatabase, cls).__new__(cls)
            cls.instance._init_connection(host, user, password, database)
        return cls.instance

    def _init_connection(self, host, user, password, database):
        super().__init__(host, user, password, database)
    
    def create_labels_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS labels (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            description TEXT,
            username VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.execute_query(query)
    
    def add_label(self, name, description, username):
        query = """
        INSERT INTO labels (name, description, username)
        VALUES (%s, %s, %s)
        """
        self.execute_query(query, (name, description, username))
    
    def get_user_labels(self, username):
        query = """
        SELECT * FROM labels WHERE username = %s
        """
        return self.fetch_all(query, (username,))
    
    def delete_label(self, label_id, username):
        query = """
        DELETE FROM labels WHERE id = %s AND username = %s
        """
        self.execute_query(query, (label_id, username))
    
    def update_label(self, label_id, name, description, username):
        query = """
        UPDATE labels SET name = %s, description = %s
        WHERE id = %s AND username = %s
        """
        self.execute_query(query, (name, description, label_id, username))