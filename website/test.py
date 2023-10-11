from website import db
from pandas import pd

sql_query = "SELECT * FROM current_data_F1"
df = pd.read_sql_query(sql_query, db.engine)
