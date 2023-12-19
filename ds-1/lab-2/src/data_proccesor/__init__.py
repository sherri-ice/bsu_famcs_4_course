from collections import defaultdict

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
        query = "SELECT * FROM public_tables_view;"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        filtered_table_names = [tup for tup in result if tup[0] != 'table_names_aliases']
        return filtered_table_names

    def _get_linked_tables_info(self, table_name):
        query = (f"SELECT "
                 f"table_name, column_name, foreign_table_name, foreign_column_name "
                 f"FROM foreign_key_info_view "
                 f"WHERE table_name::text = %s;")
        self.cursor.execute(query, (table_name,))

        linked_tables_rows = self.cursor.fetchall()
        return linked_tables_rows

    def get_table_columns(self, table_name):
        # Query to retrieve column names for the specified table
        query = f"SELECT column_name FROM information_schema.columns WHERE table_name = %s;"
        self.cursor.execute(query, (table_name,))
        return [col[0] for col in self.cursor.fetchall()]

    def get_values_for_foreign_keys(self, columns):
        options_for_foreign_cols = defaultdict(dict)
        for table_name, cols in columns.items():
            for col in cols:
                alias = self._get_aliases(table_name)
                query = f"SELECT DISTINCT {alias[-2]} FROM {table_name};"
                self.cursor.execute(query)
                real_options = self.cursor.fetchall()

                options_for_foreign_cols[alias[-2]]['options'] = [col[0] for col in real_options]

                query = f"SELECT DISTINCT {col} FROM {table_name};"
                self.cursor.execute(query)
                alias_options = self.cursor.fetchall()
                options_for_foreign_cols[alias[-2]]['alias'] = col
                options_for_foreign_cols[alias[-2]]['alias_options'] = [col[0] for col in alias_options]

        return options_for_foreign_cols

    def get_filtered_columns(self, table_name):
        orig_table_cols = self.get_table_columns(table_name)
        linked_tables = self._get_linked_tables_info(table_name)
        if len(linked_tables) == 0:
            return orig_table_cols, {}

        foreign_keys = defaultdict(list)
        for table in linked_tables:
            alias = self._get_aliases(table[2])
            if table[1] in orig_table_cols:
                orig_table_cols.remove(table[1])
                foreign_keys[table[-2]].append(alias[-1])

        return orig_table_cols, foreign_keys

    def insert_row(self, table_name, column_values):
        # Construct the SQL query with explicitly named columns
        columns = ', '.join(column_values.keys())
        placeholders = ', '.join(['%s'] * len(column_values))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"

        # Execute the query with the provided values
        self.cursor.execute(query, list(column_values.values()))

        # Commit the transaction
        self.connection.commit()

    def _get_aliases(self, table_name):
        query = (f"SELECT * FROM table_names_aliases "
                 f"WHERE table_name = %s;")
        self.cursor.execute(query, (table_name,))
        return self.cursor.fetchone()

    def _format_sql_query_for_tables(self, table_name):
        orig_table_cols = self.get_table_columns(table_name)

        linked_tables = self._get_linked_tables_info(table_name)
        if len(linked_tables) == 0:
            orig_cols, foreign_cols = self.get_filtered_columns(table_name)
            foreign_cols = [item for sublist in foreign_cols.values() for item in sublist]
            return f"SELECT {', '.join(orig_cols + foreign_cols)} FROM {table_name};"
        joins = []
        selected_columns = orig_table_cols

        for table in linked_tables:
            alias = self._get_aliases(table[2])
            if table[1] in selected_columns:
                selected_columns.remove(table[1])
                selected_columns.append(alias[-1])
            joins.append(f"JOIN {table[2]} ON {table_name}.{table[1]} = {table[2]}.{table[3]}")

        base_query = f"SELECT {', '.join(selected_columns)} FROM {table_name} {' '.join(joins)};"

        return base_query

    def get_table_data(self, table_name):
        # Query to retrieve all rows and column names from the specified table
        query = self._format_sql_query_for_tables(table_name)
        self.cursor.execute(query)

        # Fetch all rows and column names
        table_data = self.cursor.fetchall()
        column_names = [desc[0] for desc in self.cursor.description]
        data = []
        for row in table_data:
            cur_data = {}
            for i in range(len(column_names)):
                cur_data[column_names[i]] = row[i]
            data.append(cur_data)

        return data
