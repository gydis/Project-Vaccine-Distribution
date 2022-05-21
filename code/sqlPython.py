'''
---------------------------------------------------------------------
Reading & Querying Data sets using dataframes
Revised JAN '21
Sami El-Mahgary /Aalto University
Copyright (c) <2021> <Sami El-Mahgary>
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
--------------------------------------------------------------------
ADDITIONAL source for PostgreSQL
-----------------
1. psycopg2 documentation: 
    https://www.psycopg.org/docs/index.html
2. comparing different methods of loading bulk data to postgreSQL:
    https://medium.com/analytics-vidhya/pandas-dataframe-to-postgresql-using-python-part-2-3ddb41f473bd

''' 
import psycopg2
from psycopg2 import Error
from sqlalchemy import create_engine, text
import pandas as pd
import numpy as np
from pathlib import Path

def run_sql_from_file(sql_file, psql_conn):
    '''
	read a SQL file with multiple stmts and process it
	adapted from an idea by JF Santos
	Note: not really needed when using dataframes.
    '''
    sql_command = ''
    for line in sql_file:
        #if line.startswith('VALUES'):        
     # Ignore commented lines
        if not line.startswith('--') and line.strip('\n'):        
        # Append line to the command string, prefix with space
           sql_command +=  ' ' + line.strip('\n')
           #sql_command = ' ' + sql_command + line.strip('\n')
        # If the command string ends with ';', it is a full statement
        if sql_command.endswith(';'):
            # Try to execute statement and commit it
            try:
                #print("running " + sql_command+".") 
                psql_conn.execute(text(sql_command))
                #psql_conn.commit()
            # Assert in case of error
            except:
                print('Error at command:'+sql_command + ".")
                ret_ =  False
            # Finally, clear command string
            finally:
                sql_command = ''           
                ret_ = True
    return ret_

def main():
    DATADIR = str(Path(__file__).parent.parent) # for relative path 
    print("Data directory: ", DATADIR)

    # In postgres=# shell: CREATE ROLE [role_name] WITH CREATEDB LOGIN PASSWORD '[pssword]'; 
    # https://www.postgresql.org/docs/current/sql-createrole.html

    database="grp10_vaccinedist"
    user='grp10'
    password='VeKQ^hLf'
    host='dbcourse2022.cs.aalto.fi'
    # use connect function to establish the connection
    try:
        # Connect the postgres database from your local machine using psycopg2
        connection = psycopg2.connect(
                                        database=database,              
                                        user=user,       
                                        password=password,   
                                        host=host
                                    )
        #connection.autocommit = True 
        # Create a cursor to perform database operations
        cursor = connection.cursor()
        # Print PostgreSQL details
        print("PostgreSQL server information")
        print(connection.get_dsn_parameters(), "\n")
        # Executing a SQL query
        cursor.execute("SELECT version();")
        # Fetch result
        record = cursor.fetchone()
        print("You are connected to - ", record, "\n")

        # Population of DB with tables:

        # Step 1: Connect to db using SQLAlchemy create_engine
        DIALECT = 'postgresql+psycopg2://'
        db_uri = "%s:%s@%s/%s" % (user, password, host, database)
        print(DIALECT+db_uri)
        engine = create_engine(DIALECT + db_uri)
        sql_file1  = open(DATADIR + '/code/sqlCreatingDatabase.sql')
        psql_conn  = engine.connect()

        #Read SQL files for CREATE TABLE 
        run_sql_from_file (sql_file1, psql_conn)

        # Read excel file and insert into DB.

        # NOTE: For some reason, the code for executing queries from an sql file ignores the case, so all tables and attributes in the DB are lower-cased. So, until this is fixed, all columns in dataframes need to be lowercased.

        # Excel file location
        excel_file = DATADIR + '/data/vaccine-distribution-data.xlsx'

        # Example code for VaccineType data:
        # sheet_name option chooses which excel sheet is read. You can use an index (from 0), its name, or a list of indices/names. None option reads all sheets, producing a dictionary (Name of sheet -> its dataframe).
        dfVaccType = pd.read_excel(excel_file, sheet_name='VaccineType')
        dfVaccType = dfVaccType.rename(columns={'ID' : 'vaccID'})
        dfVaccType = dfVaccType.rename(str.lower, axis='columns') # Make all column names lower-case

        # The dataframe df is written into an SQL table 'vaccinetype'
        dfVaccType.to_sql('vaccinetype', con=psql_conn, if_exists='append', index=False)


        # Populating Manufacturer table
        dfManuf = pd.read_excel(excel_file, sheet_name='Manufacturer')
        dfManuf = dfManuf.rename(columns={'country' : 'origin'})
        dfManuf = dfManuf.rename(columns={'phone' : 'contactNumber'})
        dfManuf = dfManuf.rename(columns={'vaccine' : 'vaccineID'})
        dfManuf = dfManuf.rename(str.lower, axis='columns') # Make all column names lower-case

        # The dataframe df is written into an SQL table 'vaccinetype'
        dfManuf.to_sql('manufacturer', con=psql_conn, if_exists='append', index=False)

        # Populating Batch table
        dfBatch = pd.read_excel(excel_file, sheet_name='VaccineBatch')

        # Save IDs and locations for storedAt
        dfStored = dfBatch[['batchID', 'location']].copy()

        dfBatch = dfBatch.rename(columns={'amount' : 'numberOfVacc'})        
        dfBatch = dfBatch.rename(columns={'type' : 'vaccType'})        
        dfBatch = dfBatch.rename(columns={'manufDate' : 'prodDate'})
        dfBatch = dfBatch.rename(columns={'expiration' : 'expDate'})
        dfBatch = dfBatch.drop(columns='location')
        dfBatch = dfBatch.rename(str.lower, axis='columns') # Make all column names lower-case

        # The dataframe df is written into an SQL table 'vaccinetype'
        dfBatch.to_sql('batch', con=psql_conn, if_exists='append', index=False)

        # Populating hospital
        dfHospital = pd.read_excel(excel_file, sheet_name='VaccinationStations')
        dfHospital = dfHospital.rename(str.lower, axis='columns')

        dfHospital.to_sql('hospital', con=psql_conn, if_exists='append', index=False)

        # Populating storedAt table
        dfStored = dfStored.rename(columns={'location' : 'hosName'})
        dfStored = dfStored.rename(str.lower, axis='columns')

        dfStored.to_sql('storedat', con=psql_conn, if_exists='append', index=False)


        # Modify the tests below if you want to see the results of your operations (or use psql to see the changes)

        # test
        # result = psql_conn.execute(""" SELECT * FROM student LIMIT 10 """ )
        # print(f'After create and insert:\n{result.fetchall()}')

        # sql_ =  """
        #        SELECT * FROM student LIMIT 10
        #        """
        # test_df = pd.read_sql_query(sql_,psql_conn)
        # print("Select 10 students from student table: ")
        # print(test_df)
        # Drop table
        # psql_conn.execute("DROP TABLE student")

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            psql_conn.close()
            # cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
main()
