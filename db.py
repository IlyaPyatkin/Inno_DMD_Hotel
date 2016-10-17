import psycopg2
import sys

con = None

try:
    con = psycopg2.connect(database='hotel', user='postgres')
    cur = con.cursor()

    # Runs the given line as a SQL transaction
    cur.execute(input())

    con.commit()
    rows = cur.fetchall()
    for row in rows:
        print(row, end="\n")


except psycopg2.DatabaseError as e:
    print('Error %s' % e)
    sys.exit(1)


finally:
    if con:
        con.close()
