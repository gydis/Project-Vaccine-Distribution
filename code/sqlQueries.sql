-- Query 6
SELECT hospital.name AS hospital_name, SUM(batch.numberofvacc) AS total_vaccines, 
SUM(case when vacctype='V01' then batch.numberofvacc else 0 end) as V01_amount,
SUM(case when vacctype='V02' then batch.numberofvacc else 0 end) as V02_amount,
SUM(case when vacctype='V03' then batch.numberofvacc else 0 end) as V03_amount
FROM batch, hospital, storedat
WHERE hospital.name = storedat.hosname
AND batch.batchid = storedat.batchid
GROUP BY hospital.name;
