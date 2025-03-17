import pprint
import mysql.connector
import glob
import json
import csv
from io import StringIO
import itertools
import datetime
class database:

    def __init__(self, purge = False):

        # Grab information from the configuration file
        self.database       = 'db'
        self.host           = '127.0.0.1'
        self.user           = 'master'
        self.port           = 3306
        self.password       = 'master'

    def query(self, query = "SELECT CURDATE()", parameters = None):

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

    def about(self, nested=False):    
        query = """select concat(col.table_schema, '.', col.table_name) as 'table',
                          col.column_name                               as column_name,
                          col.column_key                                as is_key,
                          col.column_comment                            as column_comment,
                          kcu.referenced_column_name                    as fk_column_name,
                          kcu.referenced_table_name                     as fk_table_name
                    from information_schema.columns col
                    join information_schema.tables tab on col.table_schema = tab.table_schema and col.table_name = tab.table_name
                    left join information_schema.key_column_usage kcu on col.table_schema = kcu.table_schema
                                                                     and col.table_name = kcu.table_name
                                                                     and col.column_name = kcu.column_name
                                                                     and kcu.referenced_table_schema is not null
                    where col.table_schema not in('information_schema','sys', 'mysql', 'performance_schema')
                                              and tab.table_type = 'BASE TABLE'
                    order by col.table_schema, col.table_name, col.ordinal_position;"""
        results = self.query(query)
        if nested == False:
            return results

        table_info = {}
        for row in results:
            table_info[row['table']] = {} if table_info.get(row['table']) is None else table_info[row['table']]
            table_info[row['table']][row['column_name']] = {} if table_info.get(row['table']).get(row['column_name']) is None else table_info[row['table']][row['column_name']]
            table_info[row['table']][row['column_name']]['column_comment']     = row['column_comment']
            table_info[row['table']][row['column_name']]['fk_column_name']     = row['fk_column_name']
            table_info[row['table']][row['column_name']]['fk_table_name']      = row['fk_table_name']
            table_info[row['table']][row['column_name']]['is_key']             = row['is_key']
            table_info[row['table']][row['column_name']]['table']              = row['table']
        return table_info



    def createTables(self, purge=False, data_path = 'flask_app/database/create_tables/'):
        print('I create and populate database tables.')

        if purge:
            self.query("DROP TABLE IF EXISTS feedback")
            self.query("DROP TABLE IF EXISTS skills")
            self.query("DROP TABLE IF EXISTS experiences")
            self.query("DROP TABLE IF EXISTS positions")
            self.query("DROP TABLE IF EXISTS institutions")

        ordered_sql_files = [
        "institutions.sql",
        "positions.sql",
        "experiences.sql",
        "skills.sql",
        "feedback.sql"
        ]

        for file_name in ordered_sql_files:
            full_path = data_path + file_name
            print(f"Processing {full_path} ...")
            with open(full_path, 'r') as file:
                sql_commands = file.read()

            # Connect to the database
            cnx = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                database=self.database,  # Make sure the DB exists, or create it first
                charset='latin1'
            )
            cursor = cnx.cursor()

            # multi=True so we can execute multiple statements in a single file if needed
            for result in cursor.execute(sql_commands, multi=True):
                # Log each statement to confirm it is running
                print("Executed:", result.statement)
            cnx.commit()
            cursor.close()
            cnx.close()




    def insertRows(self, table='table', columns=['x','y'], parameters=[['v11','v12'],['v21','v22']]):
        # Build the column list and corresponding placeholder string for parameterized query.
        columns_str = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))
        sql_query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
            
        # Establish a connection
        cnx = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            port=self.port,
            database=self.database,
            charset='latin1'
        )
            
        cursor = cnx.cursor()
            
        # Execute the INSERT query for all provided rows.
        cursor.executemany(sql_query, parameters)
            
        # Commit changes to the database
        cnx.commit()
            
        cursor.close()
        cnx.close()

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

    def populateTables(self, data_path='flask_app/database/initial_data/'):
        # 1) Institutions
        with open(data_path + 'institutions.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            parameters = []
            # columns in the same order they appear in your DB table
            columns = ["name", "city", "state", "type", "address", "zip", "department"]
            for row in reader:
                # Build a single row of parameters in the same order as 'columns'
                param_row = [

                    row["name"],
                    row["city"],
                    row["state"],
                    row["type"],
                    row["address"],
                    row["zip"],
                    row["department"]
                ]
                parameters.append(param_row)

            # Insert the data
            self.insertRows(table="institutions", columns=columns, parameters=parameters)

        # 2) Positions
        with open(data_path + 'positions.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            parameters = []
            columns = ["inst_id", "title", "responsibilities", "start_date", "end_date"]
            for row in reader:
                start_date_value = row["start_date"].strip()
                if not start_date_value or start_date_value.upper() == "NULL":
                    start_date_value = None

                end_date_value = row["end_date"].strip()
                if not end_date_value or end_date_value.upper() == "NULL":
                    end_date_value = None

                param_row = [
                # or skip if it's AUTO_INCREMENT
                    row["inst_id"],
                    row["title"],
                    row["responsibilities"],
                    start_date_value,
                    end_date_value
                ]
                parameters.append(param_row)

            self.insertRows(table="positions", columns=columns, parameters=parameters)

        # 3) Experiences
        with open(data_path + 'experiences.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            parameters = []
            columns = ["position_id", "name", "description", "hyperlink", "start_date", "end_date"]
            for row in reader:

                start_date_value = row["start_date"].strip()
                if not start_date_value or start_date_value.upper() == "NULL":
                    start_date_value = None

                end_date_value = row["end_date"].strip()
                if not end_date_value or end_date_value.upper() == "NULL":
                    end_date_value = None

                param_row = [
                    
                    row["position_id"],
                    row["name"],
                    row["description"],
                    row["hyperlink"],
                    start_date_value,
                    end_date_value
                ]
                parameters.append(param_row)

            self.insertRows(table="experiences", columns=columns, parameters=parameters)

        # 4) Skills
        with open(data_path + 'skills.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            parameters = []
            columns = ["experience_id", "name", "skill_level"]
            for row in reader:
                param_row = [
                    row["experience_id"],
                    row["name"],
                    row["skill_level"]
                ]
                parameters.append(param_row)

            self.insertRows(table="skills", columns=columns, parameters=parameters)

        # # 5) Feedback
        # with open(data_path + 'feedback.csv', 'r', encoding='utf-8') as f:
        #     reader = csv.DictReader(f)
        #     parameters = []
        #     columns = ["comment_id", "name", "email", "comment"]
        #     for row in reader:
        #         param_row = [
        #             row["comment_id"],  # or skip if it's AUTO_INCREMENT
        #             row["name"],
        #             row["email"],
        #             row["comment"]
        #         ]
        #         parameters.append(param_row)

        #     self.insertRows(table="feedback", columns=columns, parameters=parameters)
        
