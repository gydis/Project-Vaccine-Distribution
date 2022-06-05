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
import openpyxl


# NOTE TO GRADER: IF YOU WANT TO RUN THIS FILE, DON'T FORGET TO INSTALL requirements.txt.
# We added new requirements there and this file might not work without them.

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
    DATADIR = str(Path(__file__).parent.parent)  # for relative path
    print("Data directory: ", DATADIR)

    # In postgres=# shell: CREATE ROLE [role_name] WITH CREATEDB LOGIN PASSWORD '[pssword]'; 
    # https://www.postgresql.org/docs/current/sql-createrole.html

    database = "grp10_vaccinedist"
    user = 'grp10'
    password = 'VeKQ^hLf'
    host = 'dbcourse2022.cs.aalto.fi'
    # use connect function to establish the connection
    try:
        # Connect the postgres database from your local machine using psycopg2
        connection = psycopg2.connect(
            database=database,
            user=user,
            password=password,
            host=host
        )

        # Create a cursor to perform database operations
        cursor = connection.cursor()

        print("PostgreSQL server information")
        print(connection.get_dsn_parameters(), "\n")
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record, "\n")

        # Population of DB with tables:

        # Step 1: Connect to db using SQLAlchemy create_engine
        DIALECT = 'postgresql+psycopg2://'
        db_uri = "%s:%s@%s/%s" % (user, password, host, database)
        print(DIALECT + db_uri)

        engine = create_engine(DIALECT + db_uri)
        psql_conn = engine.connect()

        # Read SQL files for CREATE TABLE
        if not run_sql_from_file(DATADIR + '/code/sqlCreatingDatabase.sql', psql_conn):
            return

        # Read excel file and insert into DB.

        # NOTE: For some reason, the code for executing queries from an sql file ignores the case,
        # so all tables and attributes in the DB are lower-cased.
        # So, until this is fixed, all columns in dataframes need to be lowercased.

        # Excel file location
        excel_file = DATADIR + '/data/vaccine-distribution-data.xlsx'

        # Populate VaccineType -> vaccine_type
        dfVaccType = pd.read_excel(excel_file, sheet_name='VaccineType')
        dfVaccType = dfVaccType.rename(columns={
            'tempMin': 'temp_min',
            'tempMax': 'temp_max'})
        dfVaccType = dfVaccType.rename(str.lower, axis='columns')
        dfVaccType.to_sql('vaccine_type', con=psql_conn, if_exists='append', index=False)

        # Populating Manufacturer -> manufacturer
        dfManuf = pd.read_excel(excel_file, sheet_name='Manufacturer')
        dfManuf = dfManuf.rename(columns={
            'id': 'id',
            'country': 'origin',
            'vaccine': 'vaccine_type'})
        dfManuf = dfManuf.rename(str.lower, axis='columns')
        dfManuf.to_sql('manufacturer', con=psql_conn, if_exists='append', index=False)

        # Populating VaccinationStations -> hospital
        dfHospital = pd.read_excel(excel_file, sheet_name='VaccinationStations')
        dfHospital = dfHospital.rename(str.lower, axis='columns')
        dfHospital.to_sql('hospital', con=psql_conn, if_exists='append', index=False)

        # Populating VaccineBatch -> batch
        dfBatch = pd.read_excel(excel_file, sheet_name='VaccineBatch')
        dfBatch = dfBatch.rename(columns={
            'batchID': 'id',
            'amount': 'num_of_vacc',
            'type': 'vaccine_type',
            'manufDate': 'prod_date',
            'expiration': 'exp_date',
            'location': 'hospital'})
        dfBatch = dfBatch.rename(str.lower, axis='columns')
        dfBatch.to_sql('batch', con=psql_conn, if_exists='append', index=False)

        # Populating Transportation log -> transport_log
        dfLog = pd.read_excel(excel_file, sheet_name='Transportation log')
        dfLog = dfLog.rename(columns={
            'batchID': 'batch',
            'departure ': 'dep_hos',
            'arrival': 'arr_hos',
            'dateArr': 'arr_date',
            'dateDep': 'dep_date'})
        dfLog = dfLog.rename(str.lower, axis='columns')
        dfLog.to_sql('transport_log', con=psql_conn, if_exists='append', index=False)

        # Populating StaffMembers -> staff
        dfStaff = pd.read_excel(excel_file, sheet_name='StaffMembers')
        dfStaff = dfStaff.rename(columns={
            'social security number': 'ssn',
            'date of birth': 'birthday',
            'vaccination status': 'vacc_status'})
        dfStaff['vacc_status'] = dfStaff['vacc_status'].astype('bool')
        dfStaff = dfStaff.rename(str.lower, axis='columns')
        dfStaff.to_sql('staff', con=psql_conn, if_exists='append', index=False)

        # Populating Shifts -> vaccination_shift
        dfVaccShift = pd.read_excel(excel_file, sheet_name='Shifts')
        dfVaccShift = dfVaccShift.rename(columns={'station': 'hospital'})
        dfVaccShift = dfVaccShift.rename(str.lower, axis='columns')
        dfVaccShift.to_sql('vaccination_shift', con=psql_conn, if_exists='append', index=False)

        # Populating Vaccinations -> vaccination_event
        vaccine_df = pd.read_excel(excel_file, sheet_name='Vaccinations')
        vaccine_df['date'] = pd.to_datetime(vaccine_df['date'])
        vaccine_df.columns = vaccine_df.columns.str.strip()
        vaccine_df = vaccine_df.rename(columns={
            'batchID': 'batch',
            'location': 'hospital'})
        vaccine_df = vaccine_df.rename(str.lower, axis='columns')
        vaccine_df.to_sql('vaccination_event', con=psql_conn, if_exists='append', index=False)

        # Populating Patients -> patient
        dfPatient = pd.read_excel(excel_file, sheet_name='Patients')
        dfPatient = dfPatient.rename(columns={
            'ssNo': 'ssn',
            'date of birth': 'birthday'})
        dfPatient = dfPatient.rename(str.lower, axis='columns')
        dfPatient.to_sql('patient', con=psql_conn, if_exists='append', index=False)

        # Populating VaccinePatients -> vaccine_patient
        vacc_patient_df = pd.read_excel(excel_file, sheet_name='VaccinePatients')
        vacc_patient_df['date'] = pd.to_datetime(vacc_patient_df['date'])
        vacc_patient_df.columns = vacc_patient_df.columns.str.strip()
        vacc_patient_df = vacc_patient_df.rename(columns={
            'patientSsNo': 'patient',
            'location': 'hospital'})
        vacc_patient_df = vacc_patient_df.rename(str.lower, axis='columns')
        
        
        
        vacc_patient_df.to_sql('vaccine_patient', con=psql_conn, if_exists='append', index=False)

        # Populating Symptoms -> symptoms
        dfSymptoms = pd.read_excel(excel_file, sheet_name='Symptoms')
        dfSymptoms = dfSymptoms.rename(columns={'criticality': 'critical'})
        dfSymptoms = dfSymptoms.rename(str.lower, axis='columns')
        dfSymptoms['critical'] = dfSymptoms['critical'].astype('bool')
        dfSymptoms.to_sql('symptoms', con=psql_conn, if_exists='append', index=False)

        # Populating Diagnosis -> diagnosis
        dfDiagnosis = pd.read_excel(excel_file, sheet_name='Diagnosis')
        dfDiagnosis = dfDiagnosis.drop(
            dfDiagnosis[dfDiagnosis['date'].map(lambda x: not isinstance(x, datetime.datetime))].index)
        dfDiagnosis = dfDiagnosis.rename(str.lower, axis='columns')
        dfDiagnosis.to_sql('diagnosis', con=psql_conn, if_exists='append', index=False)

        #Part 3 requirement 1
        dfReq1 = dfPatient
        dfReq1 = dfReq1[['ssn', 'gender', 'birthday']]
        dfReq1 = dfReq1.merge(dfDiagnosis, left_on='ssn', right_on='patient')
        dfReq1.drop('patient', axis=1, inplace=True)
        dfReq1 = dfReq1.rename(columns={
            'birthday' : 'date_of_birth',
            'date' : 'diagnosis_date'})
        dfReq1.to_sql('patient_symptoms', con=psql_conn, index=True, if_exists='replace')

        #Part 3 requirement 2
        dfReq2 = dfPatient
        dfReq2 = dfReq2[['ssn']]
        dfReq2 = dfReq2.merge(vacc_patient_df, left_on='ssn', right_on='patient').drop('patient', axis=1)
        dfReq2 = dfReq2.merge(vaccine_df, on=['date', 'hospital'])
        dfReq2 = dfReq2.merge(dfBatch[['id', 'vaccine_type']], left_on='batch', right_on='id').drop(['hospital', 'batch', 'id'], axis=1)

        dates = pd.DataFrame()
        types = pd.DataFrame()
        grouped = dfReq2.groupby('ssn')
        for i in grouped:
            item = i[1].reset_index(0).drop('index', axis=1).reset_index(0)
            item = item.pivot(index='ssn', columns='index')
            date = item['date'].reset_index(0)
            vacctype = item['vaccine_type'].reset_index(0)
            if 1 not in date:
                date[1] = np.nan
            if 1 not in vacctype:
                vacctype[1] = np.nan
            dates = pd.concat([dates, date])
            types = pd.concat([types, vacctype])

        res = dates.merge(types, on='ssn')
        res.loc[res['0_x'] > res['1_x'], ['0_x', '1_x', '0_y', '1_y']] = res.loc[res['0_x'] > res['1_x'], ['1_x', '0_x', '1_y', '0_y']].values
        res = res.rename(columns={
            '0_x' : 'date1',
            '1_x' : 'date2',
            '0_y' : 'vaccine_type1',
            '1_y' : 'vaccine_type2'
            })
        missing = dfPatient[~dfPatient['ssn'].isin(res['ssn'])]
        missing = missing[['ssn']]
        missing['date1'] = np.nan
        missing['date2'] = np.nan
        missing['vaccine_type1'] = np.nan
        missing['vaccine_type2'] = np.nan
        res = pd.concat([res,missing])

        res.to_sql('patient_vaccine_info', con=psql_conn, index=True, if_exists='replace')

        #Part 3 requirement 3
        dfPatientSymptoms = pd.read_sql("select * from \"patient_symptoms\"", psql_conn)

        dfSymptomsMales = dfPatientSymptoms[dfPatientSymptoms.gender == 'M']
        dfSymptomsFemales = dfPatientSymptoms[dfPatientSymptoms.gender == 'F']

        topMales = dfSymptomsMales['symptom'].value_counts().index.tolist()[:3]
        topFemales = dfSymptomsFemales['symptom'].value_counts().index.tolist()[:3]

        #Part 3 requirement 4
        ageValues = ['0-9', '10-19', '20-39', '40-59', '60+']

        now = pd.Timestamp('now')
        dfPAge = dfPatient
        dfPAge['birthday'] = pd.to_datetime(dfPAge['birthday'], format='%y%m%d')
        dfPAge['age'] = (now - dfPAge['birthday']).astype('<m8[Y]')

        ageConditions = [
            (dfPAge['age'] < 10),
            (dfPAge['age'] >= 10) & (dfPAge['age'] < 20),
            (dfPAge['age'] >= 20) & (dfPAge['age'] < 39),
            (dfPAge['age'] >= 39) & (dfPAge['age'] < 59),
            (dfPAge['age'] >= 60)
        ]
        dfPAge['age_group'] = np.select(ageConditions, ageValues)

        # removing age column, as it's not required by the task
        dfPAge.drop('age', axis=1, inplace=True)

        #Part 3 requirement 5
        dfR5vacc_patient = pd.read_sql("select * from \"vaccine_patient\"", psql_conn)
        dfR5patient = dfPAge
        dfR5vacc_patient = dfR5vacc_patient.groupby(['patient'])['date'].count()
        dfR5vacc_patient = dfR5vacc_patient.reset_index()
        dfR5vacc_patient.columns = ['ssn', 'vacc_status']
        dfR5patient = dfR5patient.merge(dfR5vacc_patient, how='left', on='ssn')
        dfR5patient['vacc_status'] = dfR5patient['vacc_status'].fillna(0)
        #dfR5patient.to_sql('patient', con=psql_conn, if_exists='append', index=False)
        #print(dfR5patient)

        #Part 3 requirement 6
        dfR6patient = dfR5patient.groupby(['age_group'])['ssn'].count()
        dfR6patient = dfR6patient.reset_index()
        dfR6patient.columns = ['age_group', 'total_number']
        dfR6patientVacc_0 = dfR5patient[dfR5patient['vacc_status'] == 0].groupby(['age_group'])['ssn'].count()
        dfR6patientVacc_0 = dfR6patientVacc_0.reset_index()
        dfR6patientVacc_0.columns = ['age_group', 'vacc0']
        dfR6patientVacc_1 = dfR5patient[dfR5patient['vacc_status'] == 1].groupby(['age_group'])['ssn'].count()
        dfR6patientVacc_1 = dfR6patientVacc_1.reset_index()
        dfR6patientVacc_1.columns = ['age_group', 'vacc1']
        dfR6patientVacc_2 = dfR5patient[dfR5patient['vacc_status'] == 2].groupby(['age_group'])['ssn'].count()
        dfR6patientVacc_2 = dfR6patientVacc_2.reset_index()
        dfR6patientVacc_2.columns = ['age_group', 'vacc2']
        dfR6patient = dfR6patient.merge(dfR6patientVacc_0, how='left', on='age_group')
        dfR6patient = dfR6patient.merge(dfR6patientVacc_1, how='left', on='age_group')
        dfR6patient = dfR6patient.merge(dfR6patientVacc_2, how='left', on='age_group')
        dfR6patient.iloc[:, 2:5] = dfR6patient.iloc[:, 2:5].divide(dfR6patient.iloc[:,1], axis = 'rows')
        dfR6patient = dfR6patient.drop('total_number', 1)
        dfR6patient.rename(columns={'age_group': 'vacc_status'}, inplace=True)
        dfR6patient = dfR6patient.set_index('vacc_status')
        dfR6patient = dfR6patient.T
        #print(dfR6patient)


        #Part 3 requirement 7
        query_7 = """
        WITH PATIENTS AS
	        (SELECT SSN, PATIENT.NAME, DIAGNOSIS.SYMPTOM
		    FROM PATIENT
		    JOIN DIAGNOSIS ON PATIENT.SSN = DIAGNOSIS.PATIENT)
        SELECT PATIENTS.NAME, PATIENTS.SYMPTOM, BATCH.VACCINE_TYPE
        FROM PATIENTS
        JOIN VACCINE_PATIENT ON VACCINE_PATIENT.PATIENT = PATIENTS.SSN
        JOIN VACCINATION_EVENT ON VACCINATION_EVENT.HOSPITAL = VACCINE_PATIENT.HOSPITAL
        JOIN BATCH ON BATCH.ID = VACCINATION_EVENT.BATCH
        """
        result = pd.read_sql_query(query_7, engine)
        df_counts = result.groupby(['vaccine_type', 'symptom']).size().reset_index(name='count')
        vaccine_group = df_counts.groupby(['vaccine_type'])['count'].sum().reset_index(name='total_count')
        df_frequency = pd.merge(df_counts, vaccine_group, left_on='vaccine_type', right_on='vaccine_type', how='left')
        df_frequency['frequency'] = df_frequency.apply(lambda row: row['count'] / row['total_count'], axis=1)
        df_frequency['frequency_text'] = df_frequency.apply(lambda row: 'very common' if row['frequency'] >= 0.1
                                                        else ('common' if row['frequency'] >= 0.05 else 'rare'), axis=1)
        pivot_symptoms = df_frequency.pivot_table(values='frequency_text', index=['symptom'],
                                                  columns='vaccine_type', aggfunc='first').reset_index()
        df_symptom_freq = pd.merge(dfSymptoms, pivot_symptoms, left_on='name', right_on='symptom', how='left')
        df_symptom_freq = df_symptom_freq.drop('symptom', axis=1)
        df_symptom_freq = df_symptom_freq.fillna('-')

        #print(df_symptom_freq)

        # Part 3, Requirement 10
        query_10 = """
            -- Vaccination events where worker in question participated
            WITH ve AS (
                SELECT ve.hospital, ve.date, vs.weekday
                FROM vaccination_shift AS vs
                RIGHT JOIN vaccination_event AS ve
                ON ve.hospital = vs.hospital AND EXTRACT(isodow FROM ve.date) = (
                    -- Make sure to only include event if weekday matches with
                    -- working shift for the worker in question.
                    CASE vs.weekday
                        WHEN 'Monday' THEN 1
                        WHEN 'Tuesday' THEN 2
                        WHEN 'Wednesday' THEN 3
                        WHEN 'Thursday' THEN 4
                        WHEN 'Friday' THEN 5
                        WHEN 'Saturday' THEN 6
                        WHEN 'Sunday' THEN 7
                    END
                ) AND ve.date >= '2021-05-05' AND ve.date <= '2021-05-15'
                WHERE vs.worker = '19740919-7140'
            )

            -- Patients
            SELECT patient.ssn, patient.name
            FROM ve
            LEFT JOIN vaccine_patient AS vp
            ON vp.hospital = ve.hospital AND vp.date = ve.date
            LEFT JOIN patient
            ON patient.ssn = vp.patient

            UNION

            -- Staff members
            SELECT staff.ssn, staff.name
            FROM ve
            LEFT JOIN vaccination_shift AS vs
            ON vs.hospital = ve.hospital AND vs.weekday = ve.weekday AND vs.worker != '19740919-7140'
            LEFT JOIN staff
            ON staff.ssn = vs.worker
            GROUP BY staff.ssn, staff.name
            ;
        """
        query_10_result = pd.read_sql_query(query_10, engine)
        # print(query_10_result)

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            psql_conn.close()
            connection.close()
            print("PostgreSQL connection is closed")


main()
