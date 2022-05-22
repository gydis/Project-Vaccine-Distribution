-- Query 1

SELECT staff.ssNo, staff.name, staff.phone, staff.role, staff.vaccinationStatus, hospital.name
FROM staff, vaccination_event, shifts
WHERE vaccination_event.date = '2021-05-10' AND vaccination_shift.address = vaccination_event.location AND vaccination_shift.day = 'Monday' AND vaccination_shift.staff = staff.id

-- Query 2
SELECT staff.ssNo, staff.name, staff.birthday, staff.phone, staff.role, staff.vaccinationStatus
FROM staff, shifts
WHERE staff.id = shifts.staff AND staff.id NOT IN (SELECT staff.id FROM staff, shifts WHERE shifts.day = 'Wednesday' AND shifts.staff = staff.id)  

-- Query 6
SELECT hospital.name AS hospital_name, SUM(batch.numberofvacc) AS total_vaccines, 
SUM(case when vacctype='V01' then batch.numberofvacc else 0 end) as V01_amount,
SUM(case when vacctype='V02' then batch.numberofvacc else 0 end) as V02_amount,
SUM(case when vacctype='V03' then batch.numberofvacc else 0 end) as V03_amount
FROM batch, hospital
WHERE hospital.name = batch.location
GROUP BY hospital.name;
