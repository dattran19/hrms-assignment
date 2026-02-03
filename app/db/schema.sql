-- Placeholder: Postgres schema + FTS indexes.

CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE hr_person (
  org_id        BIGINT      NOT NULL,
  employee_id   UUID        NOT NULL DEFAULT gen_random_uuid(), -- public opaque id
  emplid        TEXT        NOT NULL,                            -- internal HR id
  first_name    TEXT        NOT NULL,
  last_name     TEXT        NOT NULL,
  display_name  TEXT        NOT NULL,
  gender        TEXT,
  birthdate     DATE,
  address       TEXT,                                            -- simplified
  email_addr    TEXT        NOT NULL,
  phone         TEXT,
  last_update_dttm TIMESTAMPTZ NOT NULL DEFAULT now(),

  PRIMARY KEY (org_id, employee_id),
  CONSTRAINT uq_hr_person_org_emplid UNIQUE (org_id, emplid),
  CONSTRAINT uq_hr_person_org_email UNIQUE (org_id, email_addr)
);

-- Search helpers
CREATE INDEX idx_hr_person_org_display_name
  ON hr_person(org_id, display_name);

CREATE INDEX idx_hr_person_email_trgm
  ON hr_person USING GIN (email_addr gin_trgm_ops);

-- Company
CREATE TABLE hr_company (
  org_id     BIGINT NOT NULL,
  company    TEXT   NOT NULL,
  descr      TEXT   NOT NULL,
  status     TEXT   DEFAULT 'A',
  PRIMARY KEY (org_id, company)
);

CREATE TABLE hr_department (
  org_id     BIGINT NOT NULL,
  deptid     TEXT   NOT NULL,
  descr      TEXT   NOT NULL,
  parent_deptid TEXT,
  status     TEXT   DEFAULT 'A',
  PRIMARY KEY (org_id, deptid)
);

CREATE TABLE hr_location (
  org_id     BIGINT NOT NULL,
  location   TEXT   NOT NULL,
  descr      TEXT   NOT NULL,
  address    TEXT,
  city       TEXT,
  country    TEXT,
  status     TEXT   DEFAULT 'A',
  PRIMARY KEY (org_id, location)
);

CREATE TABLE hr_jobcode (
  org_id     BIGINT NOT NULL,
  jobcode    TEXT   NOT NULL,
  descr      TEXT   NOT NULL,
  job_family TEXT,
  status     TEXT   DEFAULT 'A',
  PRIMARY KEY (org_id, jobcode)
);

CREATE TABLE hr_position (
  org_id        BIGINT NOT NULL,
  position_nbr  TEXT   NOT NULL,
  descr         TEXT   NOT NULL,
  reports_to_posn TEXT,
  status        TEXT   DEFAULT 'A',
  PRIMARY KEY (org_id, position_nbr)
);

-- Employment
CREATE TABLE hr_employment (
  org_id        BIGINT      NOT NULL,
  employee_id   UUID        NOT NULL,
  empl_status   TEXT        NOT NULL DEFAULT 'A',
  hire_date     DATE,
  termination_date DATE,

  company       TEXT,
  deptid        TEXT,
  location      TEXT,
  jobcode       TEXT,
  position_nbr  TEXT,

  reports_to_employee_id UUID,   -- simple hierarchy

  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),

  -- Full-text search document
  search_tsv    tsvector,

  PRIMARY KEY (org_id, employee_id),
  CONSTRAINT fk_hr_employment_person
    FOREIGN KEY (org_id, employee_id)
    REFERENCES hr_person (org_id, employee_id)
);

-- Filter & pagination indexes
CREATE INDEX idx_hr_emp_org_status
  ON hr_employment(org_id, empl_status);

CREATE INDEX idx_hr_emp_org_updated
  ON hr_employment(org_id, updated_at DESC, employee_id);

CREATE INDEX idx_hr_emp_org_manager
  ON hr_employment(org_id, reports_to_employee_id);

CREATE INDEX idx_employment_org_deptid ON hr_employment (org_id, deptid);

CREATE INDEX idx_employment_org_position ON hr_employment (org_id, position_nbr);

-- FTS index
CREATE INDEX idx_hr_emp_search_tsv
  ON hr_employment USING GIN (search_tsv);


-- FTS trigger (directory document)
CREATE OR REPLACE FUNCTION hr_employment_search_tsv_trigger()
RETURNS trigger AS $$
DECLARE
  v_name text;
  v_email text;
  v_phone text;
  v_company text;
  v_dept text;
  v_loc text;
  v_job text;
  v_pos text;
BEGIN
  SELECT display_name, email_addr, phone
    INTO v_name, v_email, v_phone
  FROM hr_person
  WHERE org_id = NEW.org_id AND employee_id = NEW.employee_id;

  SELECT descr INTO v_company
    FROM hr_company
    WHERE org_id = NEW.org_id AND company = NEW.company;

  SELECT descr INTO v_dept
    FROM hr_department
    WHERE org_id = NEW.org_id AND deptid = NEW.deptid;

  SELECT descr INTO v_loc
    FROM hr_location
    WHERE org_id = NEW.org_id AND location = NEW.location;

  SELECT descr INTO v_job
    FROM hr_jobcode
    WHERE org_id = NEW.org_id AND jobcode = NEW.jobcode;

  SELECT descr INTO v_pos
    FROM hr_position
    WHERE org_id = NEW.org_id AND position_nbr = NEW.position_nbr;

  NEW.search_tsv :=
      setweight(to_tsvector('simple', coalesce(v_name,'')), 'A')
   || setweight(to_tsvector('simple', coalesce(v_email,'')), 'A')
   || setweight(to_tsvector('simple', coalesce(v_phone,'')), 'B')
   || setweight(to_tsvector('simple', coalesce(v_company,'')), 'C')
   || setweight(to_tsvector('simple', coalesce(v_dept,'')), 'C')
   || setweight(to_tsvector('simple', coalesce(v_loc,'')), 'C')
   || setweight(to_tsvector('simple', coalesce(v_job,'')), 'C')
   || setweight(to_tsvector('simple', coalesce(v_pos,'')), 'C');

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_hr_employment_search_tsv
BEFORE INSERT OR UPDATE ON hr_employment
FOR EACH ROW
EXECUTE FUNCTION hr_employment_search_tsv_trigger();
