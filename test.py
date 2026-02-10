import cx_Oracle, os

user = os.environ["ICARUSACCOUNT"]
pwd  = os.environ["ICARUSPWD"]

for svc in ["ccdappsdev", "ccdappsd", "ccdapps", "ccdapps_dev", "ccdappsp"]:
    try:
        dsn = cx_Oracle.makedsn("ccdapps-dev.fnal.gov", 1535, service_name=svc)
        cx_Oracle.connect(user, pwd, dsn)
        print("WORKS:", svc)
        break
    except cx_Oracle.DatabaseError:
        print("FAIL:", svc)
