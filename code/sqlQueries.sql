-- Query 1
SELECT staff.ssn, staff.name, staff.phone, staff.role, staff.vacc_status, vaccination_shift.hospital
FROM staff, vaccination_event, vaccination_shift
WHERE vaccination_event.date = '2021-05-10' AND vaccination_shift.hospital = vaccination_event.hospital AND vaccination_shift.weekday = 'Monday' AND vaccination_shift.worker = staff.ssn;

-- Query 2 (Outputs identical rows without DISTINCT on staff.ssn)
SELECT DISTINCT staff.ssn, staff.name, staff.birthday, staff.phone, staff.role, staff.vacc_status
FROM staff, vaccination_shift
WHERE staff.ssn = vaccination_shift.worker AND staff.role = 'doctor' AND  staff.ssn IN (SELECT staff.ssn FROM staff, vaccination_shift WHERE vaccination_shift.weekday = 'Wednesday' AND vaccination_shift.worker = staff.ssn); 

-- Query 6
SELECT hospital.name AS hospital_name, SUM(batch.num_of_vacc) AS total_vaccines, 
SUM(case when vaccine_type='V01' then batch.num_of_vacc else 0 end) as "V01_amount",
SUM(case when vaccine_type='V02' then batch.num_of_vacc else 0 end) as "V02_amount",
SUM(case when vaccine_type='V03' then batch.num_of_vacc else 0 end) as "V03_amount"
FROM batch, hospital
WHERE hospital.name = batch.hospital
GROUP BY hospital.name;
