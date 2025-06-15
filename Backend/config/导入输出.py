import pandas as pd
from sqlalchemy import create_engine
import os

def sql_type(series):
    """根据实际内容推断字段类型"""
    series = series.dropna()
    if pd.api.types.is_integer_dtype(series):
        return "BIGINT"
    elif pd.api.types.is_float_dtype(series):
        return "FLOAT"
    elif pd.api.types.is_bool_dtype(series):
        return "BOOLEAN"
    else:
        max_len = series.astype(str).map(len).max()
        if max_len and max_len > 255:
            return "TEXT"
        return f"VARCHAR({max(max_len, 50) if max_len else 255})"

def create_table_sql(table_name, df):
    """根据 DataFrame 生成 CREATE TABLE SQL 语句，指定utf8mb4编码"""
    columns = []
    for col in df.columns:
        col_type = sql_type(df[col].dropna())
        columns.append(f"`{col}` {col_type}")
    columns_sql = ", ".join(columns)
    sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({columns_sql}) DEFAULT CHARSET=utf8mb4;"
    return sql

def extract_table_name(file_path):
    """从文件名生成合法的 MySQL 表名"""
    name = os.path.splitext(os.path.basename(file_path))[0]
    name = name.replace('-', '_').replace(' ', '_')
    # return name
    return 'students'


def upload():
    engine = create_engine(
        'mysql+pymysql://root:123456@localhost:3306/eduplatform?charset=utf8mb4',
        connect_args={'charset': 'utf8mb4'}
    )
    conn = engine.raw_connection()
    cursor = conn.cursor()

    files = [

        r'D:\projcet_LLM\EduPlatform2\Backend\config\数据\学生表\学生记录.csv'
    ]

    columns_to_clean = ['id', 'student_id', 'org_id']

    for file_path in files:
        table_name = extract_table_name(file_path)
        df = None

        # 尝试用 utf-8 读取
        try:
            df = pd.read_csv(file_path, dtype=str, encoding='utf-8', low_memory=False)
            print(f"使用编码 utf-8 读取成功: {file_path}")
        except Exception:
            # 如果失败，尝试用 gbk
            try:
                df = pd.read_csv(file_path, dtype=str, encoding='gbk', low_memory=False)
                print(f"使用编码 gbk 读取成功: {file_path}")
            except Exception as e:
                print(f"读取失败：{file_path}，错误：{e}")
                continue

        for col in columns_to_clean:
            if col in df.columns:
                df[col] = df[col].str.lstrip("'")
                df[col] = df[col].where(df[col].str.isnumeric(), other=None)
                df[col] = df[col].astype('Int64').astype(object)

        df = df.where(pd.notnull(df), None)

        if 'id' in df.columns:
            df = df[df['id'].notnull()]

        if df.empty:
            print(f"跳过空文件：{file_path}")
            continue

        # 创建表
        try:
            create_sql = create_table_sql(table_name, df)
            cursor.execute(create_sql)
            conn.commit()
            print(f"创建表成功：{table_name}")
        except Exception as e:
            print(f"创建表失败：{table_name}，错误：{e}")
            conn.rollback()
            continue

        # 插入数据
        try:
            columns = ', '.join(f"`{col}`" for col in df.columns)
            placeholders = ', '.join(['%s'] * len(df.columns))
            sql = f"REPLACE INTO `{table_name}` ({columns}) VALUES ({placeholders})"
            cursor.executemany(sql, df.values.tolist())
            conn.commit()
            print(f"导入成功：{file_path} 到表 `{table_name}`，共 {cursor.rowcount} 条")
        except Exception as e:
            print(f"导入出错：{file_path} 到表 `{table_name}`，错误信息：{e}")
            conn.rollback()

    cursor.close()
    conn.close()

upload()