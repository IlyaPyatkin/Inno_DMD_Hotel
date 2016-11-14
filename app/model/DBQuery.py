import psycopg2

password = "rudlab"


class DBQuery:
    CODE_OK = 0
    CODE_ERROR = 1

    def __init__(self, query, params=[]):
        self.result = []
        self.error = ""
        self.code = DBQuery.CODE_ERROR
        self.run(query, params)

    def run(self, query, params):
        connection = None

        try:
            connection = psycopg2.connect(database='hotel',
                                          user='postgres',
                                          password=password)
            cursor = connection.cursor()

            # Runs the given line as a SQL transaction
            cursor.execute(query, params)
            connection.commit()

            try:
                self.result = cursor.fetchall()
            except psycopg2.ProgrammingError:
                # Query didn't return any results
                self.result = []

            self.code = DBQuery.CODE_OK

        except psycopg2.DatabaseError as e:
            print(e)
            self.error = e
            self.code = DBQuery.CODE_ERROR

        finally:
            if connection:
                connection.close()


if __name__ == '__main__':
    print("Input your query:")
    dbquery = DBQuery(input())
    if dbquery.code == DBQuery.CODE_OK:
        for row in dbquery.result:
            print(row)
