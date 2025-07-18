import mysql.connector
import glob
import json
import csv
from io import StringIO
import itertools
import hashlib
import os
import cryptography
from cryptography.fernet import Fernet
from math import pow

class database:

    def __init__(self, purge = False):

        # Grab information from the configuration file
        self.database       = 'db'
        self.host           = '127.0.0.1'
        self.user           = 'master'
        self.port           = 3306
        self.password       = 'master'
        self.tables         = ['institutions', 'positions', 'experiences', 'skills','feedback', 'users']
        
        # NEW IN HW 3-----------------------------------------------------------------
        self.encryption     =  {   'oneway': {'salt' : b'averysaltysailortookalongwalkoffashortbridge',
                                                 'n' : int(pow(2,5)),
                                                 'r' : 9,
                                                 'p' : 1
                                             },
                                'reversible': { 'key' : '7pK_fnSKIjZKuv_Gwc--sZEMKn2zc8VvD6zS96XcNHE='}
                                }
        #-----------------------------------------------------------------------------

    def query(self, query = "SELECT * FROM users", parameters = None):

        cnx = mysql.connector.connect(host     = self.host,
                                      user     = self.user,
                                      password = self.password,
                                      port     = self.port,
                                      database = self.database,
                                      charset  = 'latin1'
                                     )


        if parameters is not None:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query, parameters)
        else:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query)

        # Fetch one result
        row = cur.fetchall()
        cnx.commit()

        if "INSERT" in query:
            cur.execute("SELECT LAST_INSERT_ID()")
            row = cur.fetchall()
            cnx.commit()
        cur.close()
        cnx.close()
        return row

    def createTables(self, purge=False, data_path = 'flask_app/database/'):
        ''' FILL ME IN WITH CODE THAT CREATES YOUR DATABASE TABLES.'''

        #should be in order or creation - this matters if you are using forign keys.
         
        if purge:
            for table in self.tables[::-1]:
                self.query(f"""DROP TABLE IF EXISTS {table}""")
            
        # Execute all SQL queries in the /database/create_tables directory.
        for table in self.tables:
            
            #Create each table using the .sql file in /database/create_tables directory.
            with open(data_path + f"create_tables/{table}.sql") as read_file:
                create_statement = read_file.read()
            self.query(create_statement)

            # Import the initial data
            try:
                params = []
                with open(data_path + f"initial_data/{table}.csv") as read_file:
                    scsv = read_file.read()            
                for row in csv.reader(StringIO(scsv), delimiter=','):
                    params.append(row)
                
                # Insert the data
                cols = params[0]; params = params[1:] 
                self.insertRows(table = table,  columns = cols, parameters = params)
            except:
                print('no initial data')

    def insertRows(self, table='table', columns=['x','y'], parameters=[['v11','v12'],['v21','v22']]):
        
        # Check if there are multiple rows present in the parameters
        has_multiple_rows = any(isinstance(el, list) for el in parameters)
        keys, values      = ','.join(columns), ','.join(['%s' for x in columns])
        
        # Construct the query we will execute to insert the row(s)
        query = f"""INSERT IGNORE INTO {table} ({keys}) VALUES """
        if has_multiple_rows:
            for p in parameters:
                query += f"""({values}),"""
            query     = query[:-1] 
            parameters = list(itertools.chain(*parameters))
        else:
            query += f"""({values}) """                      
        
        insert_id = self.query(query,parameters)[0]['LAST_INSERT_ID()']         
        return insert_id
    
    def getResumeData(self):
        resume_data = {}

        # Get all institutions
        institutions = self.query("SELECT * FROM institutions")
        print(institutions)
        for inst in institutions:
            # Assume institution primary key is either 'institution_id' or 'id'
            inst_id = inst['inst_id']
            resume_data[inst_id] = inst
            resume_data[inst_id]['positions'] = {}

            # Get positions for this institution
            positions = self.query("SELECT * FROM positions WHERE inst_id = %s", (inst_id,))
            for pos in positions:
                # Assume position primary key is 'position_id'
                pos_id = pos['position_id']
                resume_data[inst_id]['positions'][pos_id] = pos
                resume_data[inst_id]['positions'][pos_id]['experiences'] = {}

                # Get experiences for this position
                experiences = self.query("SELECT * FROM experiences WHERE position_id = %s", (pos_id,))
                for exp in experiences:
                    # Use experience_id as the primary key
                    exp_id = exp['experience_id']
                    resume_data[inst_id]['positions'][pos_id]['experiences'][exp_id] = exp
                    # Initialize nested dictionaries for skills and feedback
                    resume_data[inst_id]['positions'][pos_id]['experiences'][exp_id]['skills'] = {}
                    resume_data[inst_id]['positions'][pos_id]['experiences'][exp_id]['feedback'] = {}

                    # Get skills for this experience
                    skills = self.query("SELECT * FROM skills WHERE experience_id = %s", (exp_id,))
                    for skill in skills:
                        # Use skill_id as the primary key
                        skill_id = skill['skill_id']
                        resume_data[inst_id]['positions'][pos_id]['experiences'][exp_id]['skills'][skill_id] = skill

                    # # Get feedback for this experience (assuming a column 'experience_id' exists in feedback)
                    # feedbacks = self.query("SELECT * FROM feedback WHERE experience_id = %s", (exp_id,))
                    # for fb in feedbacks:
                    #     comment_id = fb['comment_id']
                    #     resume_data[inst_id]['positions'][pos_id]['experiences'][exp_id]['feedback'][comment_id] = fb
        return resume_data

#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
    # def createUser(self, email='me@email.com', password='password', role='user'):
    #     # Check if the user already exists
    #     existing = self.query("SELECT * FROM users WHERE email = %s", [email])
    #     if existing:
    #         return {'success': 0, 'message': 'User already exists.'}
            
    #     # Encrypt the password using onewayEncrypt
    #     encrypted_password = self.onewayEncrypt(password)
        
    #     # Insert the new user into the database
    #     insert_id = self.insertRows(
    #         table='users',
    #         columns=['role', 'email', 'password'],
    #         parameters=[[role, email, encrypted_password]]
    #     )
    #     return {'success': 1, 'user_id': insert_id}

    # def authenticate(self, email='me@email.com', password='password'):
    #     # Query the user record based on email
    #     results = self.query("SELECT * FROM users WHERE email = %s", [email])
    #     if not results:
    #         return {'success': 0, 'message': 'User not found.'}
        
    #     user = results[0]
    #     # Compare the stored encrypted password with the encryption of the provided password
    #     if user['password'] == self.onewayEncrypt(password):
    #         return {'success': 1, 'user_id': user['user_id'], 'role': user['role']}
    #     else:
    #         return {'success': 0, 'message': 'Password incorrect.'}

    # def onewayEncrypt(self, string):
    #     # Use scrypt to encrypt the password
    #     encrypted_string = hashlib.scrypt(string.encode('utf-8'),
    #                                       salt = self.encryption['oneway']['salt'],
    #                                       n    = self.encryption['oneway']['n'],
    #                                       r    = self.encryption['oneway']['r'],
    #                                       p    = self.encryption['oneway']['p']
    #                                       ).hex()
    #     return encrypted_string


    # def reversibleEncrypt(self, type, message):
    #     # Use Fernet for reversible encryption
    #     fernet = Fernet(self.encryption['reversible']['key'])
        
    #     if type == 'encrypt':
    #         message = fernet.encrypt(message.encode())
    #     elif type == 'decrypt':
    #         message = fernet.decrypt(message).decode()

    #     return message


