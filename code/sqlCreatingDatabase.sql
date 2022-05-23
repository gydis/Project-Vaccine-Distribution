-- For some reason, the case of tables and attributes' names is ignored. Idk what causes it...

CREATE TABLE vaccineType (
    vaccID TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    doses INT NOT NULL CONSTRAINT positive_doses CHECK (doses > 0),
    tempMin INT NOT NULL,
    tempMax INT NOT NULL
);

CREATE TABLE hospital (
    name TEXT PRIMARY KEY,
    address TEXT NOT NULL,
    phone TEXT NOT NULL
);

CREATE TABLE batch (
    batchID TEXT PRIMARY KEY, 
    numberOfVacc INT CONSTRAINT positive_num_of_vacc CHECK (numberOfVacc > 0),
    vaccType TEXT NOT NULL,
    manufacturer TEXT NOT NULL,
    prodDate DATE NOT NULL,
    expDate DATE NOT NULL,
    location TEXT REFERENCES hospital (name),
    FOREIGN KEY (vaccType) REFERENCES vaccineType (vaccID)
);

CREATE TABLE transportLog (
    batchID TEXT REFERENCES batch,
    depHos TEXT REFERENCES hospital,
    arrHos TEXT REFERENCES hospital,
    depDate TIMESTAMP,
    arrDate TIMESTAMP,
    PRIMARY KEY (batchID, depHos, arrHos, depDate, arrDate)
);

CREATE TABLE Manufacturer (
    ID TEXT PRIMARY KEY,
    origin TEXT NOT NULL,
    contactNumber TEXT NOT NULL,
    vaccineID TEXT NOT NULL
);

CREATE TABLE staff (
    ssn TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    birthday DATE NOT NULL, 
    phone TEXT NOT NULL,
    role TEXT NOT NULL,
    vacc_status INT CHECK(vacc_status == 1 OR vacc_status == 0) NOT NULL,
    hospital TEXT NOT NULL,
    FOREIGN KEY hospital REFERENCES hospital(name)
);

CREATE TABLE vaccinationshift (
    hospital TEXT NOT NULL,
    weekday TEXT NOT NULL,
    worker TEXT NOT NULL,
    PRIMARY KEY (worker, weekday, hospital),
    FOREIGN KEY(hospital) REFERENCES hospital(name),
    FOREIGN KEY(worker) REFERENCES staff(ssn)
);

CREATE TABLE vaccination_event (
    date        date,
    location    TEXT NOT NULL,
    batchid   TEXT NOT NULL,
    PRIMARY KEY(date, location),
    FOREIGN KEY(location) REFERENCES hospital(name),
    FOREIGN KEY(batchid) REFERENCES batch(batchid)
);

CREATE TABLE vaccine_patient (
    patientssn TEXT,
    date        date NOT NULL,
    location    TEXT NOT NULL,
    PRIMARY KEY(patientssn, date)
);

CREATE TABLE IF NOT EXISTS patient (
    ssn TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    birthday DATE NOT NULL,
    gender CHAR(1) NOT NULL
);

CREATE TABLE IF NOT EXISTS symptoms (
    name TEXT PRIMARY KEY,
    critical INT NOT NULL
);

CREATE TABLE IF NOT EXISTS diagnosis (
    ssn TEXT NOT NULL,
    symptom TEXT NOT NULL,
    date DATE NOT NULL,
    PRIMARY KEY(ssn, symptom, date),
    FOREIGN KEY(ssn) REFERENCES patient(ssn),
    FOREIGN KEY(symptom) REFERENCES symptoms(name)
);

-- Command to drop all the relations (I'll just store it here for convenience.)
-- DROP TABLE batch,hospital,manufacturer,staff,vaccinationshift,transportlog,vaccinetype,vaccination_event,vaccine_patient,diagnosis, patient, symptoms;

