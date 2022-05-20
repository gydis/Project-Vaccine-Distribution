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
    depDate TIMESTAMP,
    arrDate TIMESTAMP,
    batchID TEXT REFERENCES batch,
    depHos TEXT REFERENCES hospital,
    arrHos TEXT REFERENCES hospital,
    PRIMARY KEY (batchID, depHos, arrHos, depDate, arrDate)
);
