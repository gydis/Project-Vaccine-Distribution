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
import datetime

def run_sql_from_file(file_path, conn):
    '''
    Read and run SQL queries from a file at file_path.
    '''
    ok = True
    with open(file_path, 'r') as file:
        sql_cmd = ''
        for line in file:
            i = line.find('--')
            if i != -1:
                line = line[:i]
            line = line.strip()
            if line == '':
                # Empty or comment-only line
                continue

            sql_cmd += ' ' + line
            if line.endswith(';'):
                try:
                    conn.execute(text(sql_cmd))
                except Exception as e:
                    print(f'\nError while executing SQL:\n{e}\n')
                    ok = False
                sql_cmd = ''
    return ok

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
        if not run_sql_from_file(DATADIR + '/code/sqlCreatingDatabase.sql', psql_conn):
            return

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

        dfManuf.to_sql('manufacturer', con=psql_conn, if_exists='append', index=False)

        # Populating hospital
        dfHospital = pd.read_excel(excel_file, sheet_name='VaccinationStations')
        dfHospital = dfHospital.rename(str.lower, axis='columns')

        dfHospital.to_sql('hospital', con=psql_conn, if_exists='append', index=False)

        # Populating Batch table
        dfBatch = pd.read_excel(excel_file, sheet_name='VaccineBatch')

        dfBatch = dfBatch.rename(columns={'amount' : 'numberOfVacc'})        
        dfBatch = dfBatch.rename(columns={'type' : 'vaccType'})        
        dfBatch = dfBatch.rename(columns={'manufDate' : 'prodDate'})
        dfBatch = dfBatch.rename(columns={'expiration' : 'expDate'})
        dfBatch = dfBatch.rename(str.lower, axis='columns') # Make all column names lower-case

        dfBatch.to_sql('batch', con=psql_conn, if_exists='append', index=False)

        # Populating transportLog table
        dfLog = pd.read_excel(excel_file, sheet_name='Transportation log')
        dfLog = dfLog.rename(columns={'departure ' : 'depHos', 'arrival' : 'arrHos', 'dateArr' : 'arrDate', 'dateDep' : 'depDate'})
        dfLog = dfLog.rename(str.lower, axis='columns')

        dfLog.to_sql('transportlog', con=psql_conn, if_exists='append', index=False)

        # Populating Staff table
        dfStaff = pd.read_excel(
            DATADIR + '/data/vaccine-distribution-data.xlsx', sheet_name='StaffMembers')
        dfStaff = dfStaff.rename(
            columns={'social security number': 'ssN',
                     'date of birth': 'birthday', 'vaccination status': 'vaccStatus'}
        )
        dfStaff['vaccStatus']= dfStaff['vaccStatus'].astype('bool')
        dfStaff = dfStaff.rename(str.lower, axis='columns')

        dfStaff.to_sql('staff', con=psql_conn, if_exists='append', index=False)

        # Populating Shift table
        dfVaccShift = pd.read_excel(
            DATADIR + '/data/vaccine-distribution-data.xlsx', sheet_name='Shifts')
        dfVaccShift = dfVaccShift.rename(columns={'station': 'hospital'})
        dfVaccShift = dfVaccShift.rename(str.lower, axis='columns')
        dfVaccShift.to_sql('vaccinationshift', con=psql_conn,
                           if_exists='append', index=False)

        # Populating Vaccination table
        vaccine_df = pd.read_excel(excel_file, sheet_name='Vaccinations')
        vaccine_df['date'] = pd.to_datetime(vaccine_df['date'])
        vaccine_df.columns = vaccine_df.columns.str.strip()
        vaccine_df = vaccine_df.rename(columns={'batchID': 'batchid'})
        vaccine_df = vaccine_df.rename(str.lower, axis='columns')

        vaccine_df.to_sql('vaccination_event', con=psql_conn, if_exists='append', index=False)

        # Populating Vaccine Patients
        vacc_patient_df = pd.read_excel(excel_file, sheet_name='VaccinePatients')
        vacc_patient_df['date'] = pd.to_datetime(vacc_patient_df['date'])
        vacc_patient_df.columns = vacc_patient_df.columns.str.strip()
        vacc_patient_df = vacc_patient_df.rename(columns={'patientSsNo': 'patientssn'})
        vacc_patient_df = vacc_patient_df.rename(str.lower, axis='columns')

        vacc_patient_df.to_sql('vaccine_patient', con=psql_conn, if_exists='append', index=False)

        # Populating patient info
        dfPatient = pd.read_excel(excel_file, sheet_name='Patients')
        dfPatient = dfPatient.rename(columns={
            'ssno': 'ssn',
            'date of birth': 'birthday',
        })
        dfPatient = dfPatient.rename(str.lower, axis='columns')
        dfPatient.to_sql('patient', con=psql_conn, if_exists='append', index=False)

        # Populating symptom criticality info
        dfSymptoms = pd.read_excel(excel_file, sheet_name='Symptoms')
        dfSymptoms = dfSymptoms.rename(columns={
            'criticality': 'critical',
        })
        dfSymptoms = dfSymptoms.rename(str.lower, axis='columns')
        dfSymptoms.to_sql('symptoms', con=psql_conn, if_exists='append', index=False)

        # Populating diagnosis info
        dfDiagnosis = pd.read_excel(excel_file, sheet_name='Diagnosis')
        dfDiagnosis = dfDiagnosis.rename(columns={
            'patient': 'ssn',
        })
        dfDiagnosis = dfDiagnosis.drop(dfDiagnosis[dfDiagnosis['date'].map(lambda x: not isinstance(x, datetime.datetime))].index)
        dfDiagnosis = dfDiagnosis.rename(str.lower, axis='columns')
        dfDiagnosis.to_sql('diagnosis', con=psql_conn, if_exists='append', index=False)


    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            psql_conn.close()
            # cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
main()
