import os
from flask import Flask, render_template, redirect, request, url_for
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
        # Get data and column names from the specified table
        table_data, column_names = db_proc.get_table_data(table_name)

        if table_data is not None:
            # Render the template with the table data and column names
            return render_template('table.html', table_name=table_name, table_data=table_data,
                                   column_names=column_names)
        else:
            return f"Error retrieving data from {table_name}."


@app.route('/add_row/<table_name>', methods=['GET', 'POST'])
def add_row(table_name):
    # Use the DatabaseHandler as a context manager
    with DataProcessor(conn_str) as db_proc:
        if request.method == 'POST':
            # Extract values from the form submission
            column_values = {column: request.form[column] for column in request.form}

            # Insert the new row into the specified table
            db_proc.insert_row(table_name, column_values)

            # Redirect to the table view after adding the row
            return redirect(url_for('show_table', table_name=table_name))
        else:
            # Display the form for adding a new row
            column_names = db_proc.get_filtered_columns(table_name)
            return render_template('add_row.html', table_name=table_name, column_names=column_names)


if __name__ == "__main__":
    app.run(debug=True)