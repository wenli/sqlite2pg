# SQLite to PostgreSQL Migration Tool

這是一個用於將 SQLite 資料庫遷移到 PostgreSQL 的 Python 工具。

## 功能特性

- 自動對應 SQLite 資料類型到 PostgreSQL 資料類型
- 支援表結構和資料的遷移
- 可以生成 SQL 轉儲檔案或直接匯出到 PostgreSQL 資料庫
- 處理 NULL 值、字串轉義和二進位資料

## 安裝要求

- Python 3.x
- sqlite3 (內建)
- psycopg2 (用於直接匯出到 PostgreSQL)

安裝依賴：
```bash
pip install psycopg2-binary
```

## 使用方法

### 生成 SQL 轉儲檔案

```bash
python migrate.py
```

這將從 `shi.db` SQLite 資料庫生成 `shi_pg.sql` PostgreSQL SQL 檔案。

### 直接匯出到 PostgreSQL

```bash
python migrate.py --direct --pg-url "postgresql://username:password@localhost:5432/database"
```

替換 `username`、`password`、`localhost:5432` 和 `database` 為您的 PostgreSQL 連線資訊。

## 配置

在 `migrate.py` 檔案中修改以下變數：

- `sqlite_db`: SQLite 資料庫檔案路徑
- `output_sql`: 輸出 SQL 檔案路徑

## 資料類型對應

- INTEGER → INTEGER
- REAL/FLOAT/DOUBLE → REAL
- TEXT/CHAR/CLOB → TEXT
- BLOB → BYTEA

## 注意事項

- 確保 SQLite 資料庫檔案存在且可存取
- 對於直接匯出，確保 PostgreSQL 資料庫可連線
- 工具會覆蓋目標表（如果存在）

## 許可證

請查看 LICENSE 檔案。