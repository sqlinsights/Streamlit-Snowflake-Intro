USE ROLE SECURITYADMIN;
CREATE USER SVC_STREAMLIT
PASSWORD = '';


CREATE ROLE RL_STREAMLIT;
GRANT ROLE RL_STREAMLIT TO USER SVC_STREAMLIT;
GRANT ROLE RL_STREAMLIT TO ROLE SYSADMIN;
GRANT ROLE RL_STREAMLIT TO USER SQLINSIGHTS;

USE ROLE SYSADMIN;
CREATE DATABASE IOT_DATA;
CREATE SCHEMA IOT_DATA.INGEST;

CREATE WAREHOUSE WH_STREAMLIT_APP
WAREHOUSE_SIZE = 'XSMALL'
AUTO_SUSPEND = 300
AUTO_RESUME = TRUE;


GRANT USAGE ON WAREHOUSE WH_STREAMLIT_APP TO ROLE RL_STREAMLIT;

USE ROLE SECURITYADMIN;
GRANT USAGE ON DATABASE IOT_DATA TO ROLE RL_STREAMLIT;
GRANT USAGE ON SCHEMA IOT_DATA.INGEST TO ROLE RL_STREAMLIT;
GRANT SELECT ON FUTURE TABLES IN SCHEMA IOT_DATA.INGEST TO ROLE RL_STREAMLIT;