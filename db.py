import psycopg2
import sys


def run_query(query):
    connection = None
    # print("Insert DB password:")
    # password = input()
    password = "rudlab"

    try:
        connection = psycopg2.connect(database='hotel', user='postgres', password=password)
        cursor = connection.cursor()

        # Runs the given line as a SQL transaction
        cursor.execute(query)
        connection.commit()
        output = cursor.fetchall()

    except psycopg2.DatabaseError as e:
        print('Error %s' % e)
        sys.exit(1)

    finally:
        if connection:
            connection.close()

    return output

if __name__ == '__main__':
    print("Input your query:")
    for row in run_query(input()):
        print(row)
