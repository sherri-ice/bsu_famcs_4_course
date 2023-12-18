import os
from flask import Flask, render_template
from dotenv import load_dotenv
from data_proccesor import DataProcessor

load_dotenv()

conn_str = os.getenv("DB_URI")

app = Flask(__name__)


@app.route('/')
def index():
    with DataProcessor(conn_str) as db_proc:
        table_names = db_proc.get_table_names()

        if table_names is not None:
            # Render the templates with the table names
            return render_template('index.html', table_names=table_names)
        else:
            return "Error connecting to the database."


@app.route('/table/<table_name>')
def show_table(table_name):
    # Use the DatabaseHandler as a context manager
    with DataProcessor(conn_str) as db_proc:
        # Get data from the specified table
        table_data = db_proc.get_table_data(table_name)

        if table_data is not None:
            # Render the template with the table data
            return render_template('table.html', table_name=table_name, table_data=table_data)
        else:
            return f"Error retrieving data from {table_name}."


if __name__ == "__main__":
    app.run(debug=True)
