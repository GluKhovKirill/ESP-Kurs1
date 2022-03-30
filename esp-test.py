#  pip install psycopg2
# sudo apt-get install python3-psycopg2
import psycopg2





connect_str = "dbname='esp_db' user='esp_user' host='localhost' password='mypwd'"
    # use our connection values to establish a connection
conn = psycopg2.connect(connect_str)
    

cur = conn.cursor()
cur.execute("select * from coursework.users")
rows = cur.fetchall()
print(rows)
conn.close()