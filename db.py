import psycopg2


def run_query(query):
    connection = None
    code = "Error"
    password = "rudlab"

    try:
        connection = psycopg2.connect(database='hotel', user='postgres', password=password)
        cursor = connection.cursor()

        # Runs the given line as a SQL transaction
        cursor.execute(query)
        connection.commit()
        output = cursor.fetchall()
        code = "Success"

    except psycopg2.DatabaseError as e:
        print('Error %s' % e)
        output = e

    finally:
        if connection:
            connection.close()

    return code, output


if __name__ == '__main__':
    print("Input your query:")
    for row in run_query(input())[1]:
        print(row)
