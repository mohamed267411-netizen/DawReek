use footballDB

select * from Teams

-- تعديل نيوكاسل
UPDATE Teams 
SET teamname = 'Sheffield' 
WHERE teamID = 15;
-- تعديل توتنهام
UPDATE Teams 
SET teamname = 'Tottenham' 
WHERE teamID = 17;

-- تعديل نيوكاسل
UPDATE Teams 
SET teamname = 'Newcastle' 
WHERE teamID = 14;

-- تعديل ولفرهامبتون (لاختصاره)
UPDATE Teams 
SET teamname = 'Wolves' 
WHERE teamID = 19;

-- تعديل برايتون
UPDATE Teams 
SET teamname = 'Brighton' 
WHERE teamID = 5;

-- تعديل مانشستر سيتي
UPDATE Teams 
SET teamname = 'Man City' 
WHERE teamID = 12;

-- تعديل مانشستر يونايتد
UPDATE Teams 
SET teamname = 'Man United' 
WHERE teamID = 13;



-- 1. إضافة العمود
ALTER TABLE Teams ADD teamLogo NVARCHAR(MAX);
GO

-- 2. تحديث المسارات (بناءً على الصورة التانية اللي بعتها)
UPDATE Teams SET teamLogo = 'imag\logo\arsenal-footballlogos-org.png' WHERE teamname = 'Arsenal';
UPDATE Teams SET teamLogo = 'imag\logo\liverpool-fc-footballlogos-org.png' WHERE teamname = 'Liverpool';
UPDATE Teams SET teamLogo = 'imag\logo\manchester-city-footballlogos-org.png' WHERE teamname = 'Man City';
UPDATE Teams SET teamLogo = 'imag\logo\manchester-united-footballlogos-org.png' WHERE teamname = 'Man United';
UPDATE Teams SET teamLogo = 'imag\logo\wolverhampton-footballlogos-org.png' WHERE teamname = 'Wolves';
UPDATE Teams SET teamLogo = 'imag\logo\aston-villa-footballlogos-org.png' WHERE teamname = 'Aston villa';
UPDATE Teams SET teamLogo = 'imag\logo\bournemouth-footballlogos-org.png' WHERE teamname = 'Bournemouth';
UPDATE Teams SET teamLogo = 'imag\logo\brentford-footballlogos-org.png' WHERE teamname = 'Brentford';
UPDATE Teams SET teamLogo = 'imag\logo\brighton-hove-footballlogos-org.png' WHERE teamname = 'Brighton';
UPDATE Teams SET teamLogo = 'imag\logo\burnley-footballlogos-org.png' WHERE teamname = 'Burnley';
UPDATE Teams SET teamLogo = 'imag\logo\chelsea-footballlogos-org.png' WHERE teamname = 'Chelsea';
UPDATE Teams SET teamLogo = 'imag\logo\crystal-palace-footballlogos-org.png' WHERE teamname = 'Crystal Palace';
UPDATE Teams SET teamLogo = 'imag\logo\everton-footballlogos-org.png' WHERE teamname = 'Everton';
UPDATE Teams SET teamLogo = 'imag\logo\fulham-footballlogos-org.png' WHERE teamname = 'Fulham';
UPDATE Teams SET teamLogo = 'imag\logo\england_newcastle_1500x1500.png' WHERE teamname = 'Newcastle';
UPDATE Teams SET teamLogo = 'imag\logo\sheffield-wednesday-footballlogos-org.png' WHERE teamname = 'Sheffield';
UPDATE Teams SET teamLogo = 'imag\logo\southampton-footballlogos-org.png' WHERE teamname = 'Southampton';
UPDATE Teams SET teamLogo = 'imag\logo\tottenham-hotspur-footballlogos-org.png' WHERE teamname = 'Tottenham';
UPDATE Teams SET teamLogo = 'imag\logo\watford-footballlogos-org.png' WHERE teamname = 'watford';






-- كمل باقي الفرق بنفس النمط