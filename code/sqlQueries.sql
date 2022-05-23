-- Query 1
SELECT staff.ssn, staff.name, staff.phone, staff.role, staff.vaccstatus, vaccinationshift.hospital
FROM staff, vaccination_event, vaccinationshift
WHERE vaccination_event.date = '2021-05-10' AND vaccinationshift.hospital = vaccination_event.location AND vaccinationshift.weekday = 'Monday' AND vaccinationshift.worker = staff.ssn;

-- Query 2
SELECT staff.ssn, staff.name, staff.birthday, staff.phone, staff.role, staff.vaccstatus
FROM staff, vaccinationshift
WHERE staff.ssn = vaccinationshift.worker AND staff.role = 'doctor' AND  staff.ssn IN (SELECT staff.ssn FROM staff, vaccinationshift WHERE vaccinationshift.weekday = 'Wednesday' AND vaccinationshift.worker = staff.ssn); 

-- Query 6
SELECT hospital.name AS hospital_name, SUM(batch.numberofvacc) AS total_vaccines, 
SUM(case when vacctype='V01' then batch.numberofvacc else 0 end) as V01_amount,
SUM(case when vacctype='V02' then batch.numberofvacc else 0 end) as V02_amount,
SUM(case when vacctype='V03' then batch.numberofvacc else 0 end) as V03_amount
FROM batch, hospital
WHERE hospital.name = batch.location
GROUP BY hospital.name;
