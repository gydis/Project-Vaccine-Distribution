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
    FOREIGN KEY (vaccType) REFERENCES vaccineType (vaccID)
);

CREATE TABLE storedAt (
    batchID TEXT PRIMARY KEY,
    hosName TEXT,
    FOREIGN KEY (batchID) REFERENCES batch (batchID),
    FOREIGN KEY (hosName) REFERENCES hospital (name)
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

CREATE TABLE Staff (
    ssN TEXT PRIMARY KEY,
    name TEXT,
    birthday DATE, -- TEXT?
    vaccStatus INT CHECK(vaccinationStatus == 1 OR vaccinationStatus == 0),
    -- vaccinationStatus BOOLEAN, 
    role TEXT
);

CREATE TABLE VaccinationShift (
    weekday TEXT,
    FOREIGN KEY hospital REFERENCES hospital (name),
    PRIMARY KEY (weekday, hospital)
);

-- Command to drop all the relations (I'll just store it here for convenience.)
-- DROP TABLE batch,hospital,manufacturer,storedat,transportlog,vaccinetype;

