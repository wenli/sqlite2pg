import sqlite3
import argparse

# SQLite database path
sqlite_db = 'shi.db'

# Output SQL file
output_sql = 'shi_pg.sql'

def map_type(sqlite_type):
    sqlite_type = sqlite_type.upper()
    if 'INT' in sqlite_type:
        return 'INTEGER'
    elif 'REAL' in sqlite_type or 'FLOAT' in sqlite_type or 'DOUBLE' in sqlite_type:
        return 'REAL'
    elif 'TEXT' in sqlite_type or 'CHAR' in sqlite_type or 'CLOB' in sqlite_type:
        return 'TEXT'
    elif 'BLOB' in sqlite_type:
        return 'BYTEA'
    else:
        return 'TEXT'  # Fallback for unrecognized types

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

def migrate(direct_export=False, pg_url=None):
    # Connect to SQLite
    conn_sqlite = sqlite3.connect(sqlite_db)
    cursor_sqlite = conn_sqlite.cursor()

    if direct_export:
        import psycopg2
        conn_pg = psycopg2.connect(pg_url)
        cursor_pg = conn_pg.cursor()
    else:
        f = open(output_sql, 'w', encoding='utf-8')

    # Get all tables
    cursor_sqlite.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = cursor_sqlite.fetchall()

    for table in tables:
        table_name = table[0]
        print(f"Processing table: {table_name}")

        # Get table info
        cursor_sqlite.execute(f"PRAGMA table_info({table_name})")
        columns = cursor_sqlite.fetchall()

        # Sample data to determine actual column types
        cursor_sqlite.execute(f"SELECT * FROM {table_name} LIMIT 10")
        sample_rows = cursor_sqlite.fetchall()
        col_types = []
        for i in range(len(columns)):
            if not sample_rows:
                # No data, use declared type
                declared_type = columns[i][2]
                col_types.append(map_type(declared_type))
            else:
                types_in_col = set(type(row[i]) for row in sample_rows)
                if len(types_in_col) == 1:
                    t = types_in_col.pop()
                    if t == int:
                        col_types.append('INTEGER')
                    elif t == float:
                        col_types.append('REAL')
                    elif t == str:
                        col_types.append('TEXT')
                    elif t == bytes:
                        col_types.append('BYTEA')
                    else:
                        col_types.append('TEXT')
                else:
                    col_types.append('TEXT')  # Mixed types

        # Build CREATE TABLE statement
        create_stmt = f'CREATE TABLE "{table_name}" ('
        col_defs = []
        for col in columns:
            cid, name, declared_type, notnull, default, pk = col
            type_pg = col_types[cid]
            col_def = f'"{name}" {type_pg}'
            if pk:
                col_def += " PRIMARY KEY"
            if notnull:
                col_def += " NOT NULL"
            if default is not None:
                col_def += f" DEFAULT {default}"
            col_defs.append(col_def)
        create_stmt += ", ".join(col_defs) + ");\n"

        if direct_export:
            drop_stmt = f'DROP TABLE IF EXISTS "{table_name}";'
            cursor_pg.execute(drop_stmt)
            cursor_pg.execute(create_stmt)
        else:
            f.write(create_stmt)

        # Get data
        cursor_sqlite.execute(f"SELECT * FROM {table_name}")
        rows = cursor_sqlite.fetchall()

        if rows:
            # Get column names
            col_names = [col[1] for col in columns]
            quoted_col_names = [f'"{n}"' for n in col_names]
            for row in rows:
                if direct_export:
                    insert_stmt = f'INSERT INTO "{table_name}" ({", ".join(quoted_col_names)}) VALUES ({", ".join(["%s"] * len(row))})'
                    cursor_pg.execute(insert_stmt, row)
                else:
                    values = [escape_value(val) for val in row]
                    insert_stmt = f'INSERT INTO "{table_name}" ({", ".join(quoted_col_names)}) VALUES ({", ".join(values)});\n'
                    f.write(insert_stmt)

    if direct_export:
        conn_pg.commit()
        conn_pg.close()
        print("Direct export to PostgreSQL completed")
    else:
        f.close()
        print(f"SQL dump created: {output_sql}")

    conn_sqlite.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate SQLite database to PostgreSQL")
    parser.add_argument('--direct', action='store_true', help='Direct export to PostgreSQL')
    parser.add_argument('--pg-url', type=str, help='PostgreSQL connection URL')
    args = parser.parse_args()
    #& C:/Intel/sqlite2pg/.venv/Scripts/python.exe c:/Intel/sqlite2pg/migrate.py --direct --pg-url postgresql://wenli:1qazxsw2@localhost:5432/sk_stock  
    if args.direct:
        if not args.pg_url:
            print("Error: --pg-url is required when using --direct")
            exit(1)
        migrate(direct_export=True, pg_url=args.pg_url)
    else:
        migrate()