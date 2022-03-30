#  pip install psycopg2
# sudo apt-get install python3-psycopg2
# pip install psycopg2-binary
import psycopg2





connect_str = "dbname='iu25' user='airflow' host='172.18.0.3' password='airflow'"
    # use our connection values to establish a connection
conn = psycopg2.connect(connect_str)
    

cur = conn.cursor()
cur.execute("select * from public.logistics")
rows = cur.fetchall()
print(rows)
conn.close()