import psycopg2


class DataProcessor:

    def __init__(self, conn_str: str):
        self.conn_str = conn_str

    def __enter__(self):
        self.connection = psycopg2.connect(self.conn_str)
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cursor.close()
        self.connection.close()

    def get_table_names(self):
        # Query to retrieve table names in the public schema
        query = "SELECT * FROM public_tables_view;"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_table_data(self, table_name):
        # Query to retrieve all rows from the specified table
        query = f"SELECT * FROM {table_name};"
        self.cursor.execute(query)
        return self.cursor.fetchall()
