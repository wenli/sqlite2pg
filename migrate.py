import sqlite3

# SQLite database path
sqlite_db = 'shi.db'

# Output SQL file
output_sql = 'shi_pg.sql'

def map_type(sqlite_type):
    sqlite_type = sqlite_type.upper()
    if sqlite_type in ['INTEGER', 'INT']:
        return 'INTEGER'
    elif sqlite_type in ['TEXT', 'VARCHAR', 'NVARCHAR']:
        return 'TEXT'
    elif sqlite_type == 'REAL':
        return 'REAL'
    elif sqlite_type == 'BLOB':
        return 'BYTEA'
    elif sqlite_type == 'NUMERIC':
        return 'NUMERIC'
    else:
        return 'TEXT'  # Default

def escape_value(value):
    if value is None:
        return 'NULL'
    elif isinstance(value, str):
        escaped = value.replace("'", "''")
        return f"'{escaped}'"
    elif isinstance(value, bytes):
        return f"'\\x{value.hex()}'"  # For BYTEA
    else:
        return str(value)

def migrate():
    # Connect to SQLite
    conn_sqlite = sqlite3.connect(sqlite_db)
    cursor_sqlite = conn_sqlite.cursor()

    with open(output_sql, 'w', encoding='utf-8') as f:
        # Get all tables
        cursor_sqlite.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = cursor_sqlite.fetchall()

        for table in tables:
            table_name = table[0]
            print(f"Processing table: {table_name}")

            # Get table info
            cursor_sqlite.execute(f"PRAGMA table_info({table_name})")
            columns = cursor_sqlite.fetchall()

            # Build CREATE TABLE statement
            create_stmt = f'CREATE TABLE "{table_name}" ('
            col_defs = []
            for col in columns:
                cid, name, type, notnull, default, pk = col
                type_pg = map_type(type)
                col_def = f'"{name}" {type_pg}'
                if pk and type.upper() == 'INTEGER':
                    col_def = f'"{name}" SERIAL PRIMARY KEY'
                else:
                    if pk:
                        col_def += " PRIMARY KEY"
                if notnull:
                    col_def += " NOT NULL"
                if default is not None:
                    col_def += f" DEFAULT {default}"
                col_defs.append(col_def)
            create_stmt += ", ".join(col_defs) + ");\n"

            f.write(create_stmt)

            # Get data
            cursor_sqlite.execute(f"SELECT * FROM {table_name}")
            rows = cursor_sqlite.fetchall()

            if rows:
                # Get column names
                col_names = [col[1] for col in columns]
                quoted_col_names = [f'"{n}"' for n in col_names]
                for row in rows:
                    values = [escape_value(val) for val in row]
                    insert_stmt = f'INSERT INTO "{table_name}" ({", ".join(quoted_col_names)}) VALUES ({", ".join(values)});\n'
                    f.write(insert_stmt)

    conn_sqlite.close()
    print(f"SQL dump created: {output_sql}")

if __name__ == "__main__":
    migrate()