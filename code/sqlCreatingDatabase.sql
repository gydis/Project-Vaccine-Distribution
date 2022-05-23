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
    ssN TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    birthday DATE NOT NULL, 
    phone TEXT NOT NULL,
    role TEXT NOT NULL,
    vaccStatus BOOLEAN NOT NULL, 
    hospital TEXT REFERENCES hospital(name) 
);

CREATE TABLE vaccinationshift (
    hospital TEXT REFERENCES hospital(name) NOT NULL,
    weekday TEXT NOT NULL,
    worker TEXT REFERENCES staff(ssN) NOT NULL,
    PRIMARY KEY (worker, weekday) 
);

CREATE TABLE vaccination_event (
    date        date,
    location    TEXT NOT NULL,
    "batchID"   TEXT NOT NULL,
    PRIMARY KEY(date, location),
    FOREIGN KEY(location) REFERENCES hospital(name),
    FOREIGN KEY("batchID") REFERENCES batch(batchid)
);

CREATE TABLE vaccine_patient (
    "patientSsNo" TEXT,
    date        date NOT NULL,
    location    TEXT NOT NULL,
    PRIMARY KEY("patientSsNo", date)
);

CREATE TABLE IF NOT EXISTS patient (
    ssN TEXT PRIMARY KEY,
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
    FOREIGN KEY(ssn) REFERENCES patient(ssN),
    FOREIGN KEY(symptom) REFERENCES symptoms(name)
);

-- Command to drop all the relations (I'll just store it here for convenience.)
-- DROP TABLE batch,hospital,manufacturer,staff,vaccinationshift,transportlog,vaccinetype,vaccination_event,vaccine_patient;

