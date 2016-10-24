import psycopg2
import sys

con = None
print("Insert DB password:")
password = input()


try:
    con = psycopg2.connect(database='hotel', user='postgres', password=password)
    cur = con.cursor()

    # Runs the given line as a SQL transaction
    print("Insert your SQL query:")
    query = input()
    cur.execute(query)

    con.commit()
    rows = cur.fetchall()
    for row in rows:
        print(row)


except psycopg2.DatabaseError as e:
    print('Error %s' % e)
    sys.exit(1)


finally:
    if con:
        con.close()
