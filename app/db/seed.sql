BEGIN;

-- 1. CLEANUP (Dev only)
-- Truncate all tables to ensure a fresh start
TRUNCATE TABLE
  hr_employment,
  hr_person,
  hr_company,
  hr_department,
  hr_location,
  hr_jobcode,
  hr_position
RESTART IDENTITY CASCADE;

-- 2. REFERENCE DATA
INSERT INTO hr_company (org_id, company, descr, status) VALUES
  (1, 'C01', 'ABC Vietnam', 'A'),
  (2, 'C01', 'ABC Singapore', 'A');

INSERT INTO hr_department (org_id, deptid, descr, status) VALUES
  (1, 'IT', 'Information Technology', 'A'), (1, 'HR', 'Human Resources', 'A'), (1, 'FIN', 'Finance', 'A'),
  (2, 'ENG', 'Engineering', 'A'), (2, 'OPS', 'Operations', 'A'), (2, 'HR', 'Human Resources', 'A');

INSERT INTO hr_location (org_id, location, descr, country, status) VALUES
  (1, 'HCM', 'Ho Chi Minh City', 'VN', 'A'), (1, 'HAN', 'Ha Noi', 'VN', 'A'),
  (2, 'SG',  'Singapore', 'SG', 'A');

INSERT INTO hr_jobcode (org_id, jobcode, descr, status) VALUES
  (1, 'DEV', 'Software Engineer', 'A'), (1, 'HRM', 'HR Manager', 'A'), (1, 'FIN', 'Finance Analyst', 'A'),
  (2, 'ENG', 'Engineer', 'A'), (2, 'OPS', 'Operations Specialist', 'A'), (2, 'HRM', 'HR Manager', 'A');

INSERT INTO hr_position (org_id, position_nbr, descr, status) VALUES
  (1, 'P100', 'IT Manager', 'A'), (1, 'P101', 'Tech Lead', 'A'), (1, 'P102', 'Senior Developer', 'A'),
  (2, 'P200', 'Engineering Manager', 'A'), (2, 'P201', 'Lead Engineer', 'A'), (2, 'P202', 'Engineer', 'A');

-- 3. PERSON DATA GENERATION
-- ORG 1 Manager (Explicit)
INSERT INTO hr_person (org_id, emplid, first_name, last_name, display_name, email_addr, phone, address)
VALUES (1, 'E00001', 'Alice', 'Nguyen', 'Alice Nguyen', 'alice.nguyen@abc.com', '090000001', 'HCM City');

-- ORG 2 Manager (Explicit)
INSERT INTO hr_person (org_id, emplid, first_name, last_name, display_name, email_addr, phone, address)
VALUES (2, 'E20001', 'Carol', 'Lim', 'Carol Lim', 'carol.lim@abc.sg', '080000001', 'Singapore');

-- Generate Org 1 (ID 2-50)
INSERT INTO hr_person (org_id, emplid, first_name, last_name, display_name, email_addr, phone, address)
SELECT 1, 'E' || lpad(gs::text, 5, '0'),
  (ARRAY['Bob','Dat','Huy','Lan','Minh','Nga','Phuc','Quang','Trang','Vy'])[(gs % 10) + 1],
  (ARRAY['Tran','Le','Pham','Ho','Vo','Dang','Nguyen','Do','Bui','Vu'])[(gs % 10) + 1],
  (ARRAY['Bob','Dat','Huy','Lan','Minh','Nga','Phuc','Quang','Trang','Vy'])[(gs % 10) + 1] || ' ' || (ARRAY['Tran','Le','Pham','Ho','Vo','Dang','Nguyen','Do','Bui','Vu'])[(gs % 10) + 1],
  'user' || gs::text || '@abc.com', '090' || lpad(gs::text, 6, '0'), 'Vietnam'
FROM generate_series(2, 50) gs;

-- Generate Org 1 Extended (ID 51-200)
INSERT INTO hr_person (org_id, emplid, first_name, last_name, display_name, email_addr, phone, address)
SELECT 1, 'E' || lpad(gs::text, 5, '0'),
  (ARRAY['Bob','Dat','Huy','Lan','Minh','Nga','Phuc','Quang','Trang','Vy'])[(gs % 10) + 1],
  (ARRAY['Tran','Le','Pham','Ho','Vo','Dang','Nguyen','Do','Bui','Vu'])[(gs % 10) + 1],
  (ARRAY['Bob','Dat','Huy','Lan','Minh','Nga','Phuc','Quang','Trang','Vy'])[(gs % 10) + 1] || ' ' || (ARRAY['Tran','Le','Pham','Ho','Vo','Dang','Nguyen','Do','Bui','Vu'])[(gs % 10) + 1],
  'user' || gs::text || '@abc.com', '090' || lpad(gs::text, 7, '0'), 'Vietnam'
FROM generate_series(51, 200) gs;

-- Generate Org 2 (ID 2-25)
INSERT INTO hr_person (org_id, emplid, first_name, last_name, display_name, email_addr, phone, address)
SELECT 2, 'E2' || lpad(gs::text, 4, '0'),
  (ARRAY['David','Ethan','Fiona','Grace','Henry','Ivy','Jason','Kelly','Liam','Maya'])[(gs % 10) + 1],
  (ARRAY['Tan','Lee','Lim','Wong','Ng','Chua','Goh','Teo','Koh','Ong'])[(gs % 10) + 1],
  (ARRAY['David','Ethan','Fiona','Grace','Henry','Ivy','Jason','Kelly','Liam','Maya'])[(gs % 10) + 1] || ' ' || (ARRAY['Tan','Lee','Lim','Wong','Ng','Chua','Goh','Teo','Koh','Ong'])[(gs % 10) + 1],
  'user' || gs::text || '@abc.sg', '080' || lpad(gs::text, 6, '0'), 'Singapore'
FROM generate_series(2, 25) gs;

-- 4. EMPLOYMENT HIERARCHY AND STATUS
WITH people_data AS (
  SELECT *, substring(emplid from 2)::int as id_num,
  row_number() OVER (PARTITION BY org_id ORDER BY emplid) AS seq
  FROM hr_person
),
managers AS ( SELECT org_id, employee_id FROM people_data WHERE seq = 1 ),
leads AS ( SELECT org_id, employee_id, seq FROM people_data WHERE seq BETWEEN 2 AND 6 )
INSERT INTO hr_employment (org_id, employee_id, empl_status, company, deptid, location, jobcode, position_nbr, reports_to_employee_id, updated_at)
SELECT
  p.org_id, p.employee_id,
  CASE 
    WHEN p.id_num <= 100 THEN 'A' 
    WHEN p.id_num <= 150 THEN 'I' 
    ELSE 'N' 
  END,
  'C01',
  (ARRAY['IT','HR','FIN'])[(p.id_num % 3) + 1],
  (ARRAY['HCM','HAN'])[(p.id_num % 2) + 1],
  (ARRAY['DEV','HRM','FIN'])[(p.id_num % 3) + 1],
  (ARRAY['P100','P101','P102'])[(p.id_num % 3) + 1],
  CASE 
    WHEN p.seq = 1 THEN NULL
    WHEN p.seq BETWEEN 2 AND 6 THEN (SELECT employee_id FROM managers m WHERE m.org_id = p.org_id)
    ELSE (SELECT l.employee_id FROM leads l WHERE l.org_id = p.org_id AND l.seq = (2 + ((p.seq - 7) % 5)) LIMIT 1)
  END,
  now() - (p.id_num * interval '1 hour')
FROM people_data p;

COMMIT;