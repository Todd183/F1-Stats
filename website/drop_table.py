# from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect,text
from .models import User

db = SQLAlchemy()
DB_NAME = "database.db"
app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
db.init_app(app)


def drop_table(table_name):
    with app.app_context():
        db.Model.metadata.reflect(bind=db.engine)
        db.Model.metadata.tables[table_name].drop(db.engine)

# Usage example to drop the "Transaction" table
if __name__ == "__main__":
    table_name_to_drop = "table_name"  # Replace with the correct table name
    drop_table(table_name_to_drop)
    print('Drop transaction')

# def get_table_names():
#     with app.app_context():
#         inspector = inspect(db.engine)
#         table_names = inspector.get_table_names()
#         return table_names

# if __name__ == "__main__":
#     table_names_to_print = get_table_names()  # List of model classes to print
#     for table_name in table_names_to_print:
#         print(table_name)

