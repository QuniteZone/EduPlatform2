import os
from sqlalchemy import create_engine
import pandas as pd
from tqdm import tqdm


# 判断字段类型
def sql_type(series):
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

# 生成建表SQL
def create_table_sql(table_name, df):
    columns = []
    for col in df.columns:
        col_type = sql_type(df[col].dropna())
        columns.append(f"`{col}` {col_type}")
    columns_sql = ", ".join(columns)
    sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({columns_sql}) DEFAULT CHARSET=utf8mb4;"
    return sql

def extract_table_name(file_path):
    name = os.path.splitext(os.path.basename(file_path))[0]
    name = name.replace('-', '_').replace(' ', '_')
    return name

# 上传文件内容到MySQL
def upload():
    engine = create_engine(
        'mysql+pymysql://root:123456@localhost:3306/eduplateform?charset=utf8mb4',
        connect_args={'charset': 'utf8mb4'}
    )
    conn = engine.raw_connection()
    cursor = conn.cursor()

    files = [
        r'C:\code\user_profile\user_profile\数据\学生表\学生记录.csv'
    ]

    columns_to_clean = ['id', 'student_id', 'org_id']

    for file_path in files:
        table_name = extract_table_name(file_path)
        df = None

        try:
            df = pd.read_csv(file_path, dtype=str, encoding='utf-8', low_memory=False)
            print(f"使用编码 utf-8 读取成功: {file_path}")
        except Exception:
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

        try:
            create_sql = create_table_sql(table_name, df)
            cursor.execute(create_sql)
            conn.commit()
            print(f"创建表成功：{table_name}")
        except Exception as e:
            print(f"创建表失败：{table_name}，错误：{e}")
            conn.rollback()
            continue

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



# 按照lesson_id合并学习记录和学习任务
def join():
    engine = create_engine("mysql+pymysql://root:123456@localhost:3306/eduplatform?charset=utf8mb4")

    # 读取学习记录
    study_record_df = pd.read_sql("""
        SELECT create_by, lesson_id, study_time, status, create_time
        FROM studylog
    """, engine)
    print("已读取 study_record")

    # 读取学习任务
    task_df = pd.read_sql("""
        SELECT lesson_id, task_type
        FROM course_task
    """, engine)
    print("已读取 course_lesson_task")

    # 对 task_df 以 lesson_id 分组，合并 task_type（去重），拼接成字符串
    task_grouped = task_df.groupby('lesson_id')['task_type'] \
        .apply(lambda x: ",".join(sorted(map(str, x.unique())))) \
        .reset_index()
    print("已合并重复的 task_type")

    # 左连接学习记录和合并后的任务类型表
    merged_df = pd.merge(
        study_record_df,
        task_grouped,
        on='lesson_id',
        how='left'
    )
    print("已完成左连接")

    # 保留所需字段
    result_df = merged_df[['create_by', 'lesson_id', 'study_time', 'status', 'create_time', 'task_type']]

    # 写入数据库新表
    table_name = "study_recore_task_test"
    chunksize = 5000
    total_chunks = len(result_df) // chunksize + 1

    with engine.begin() as conn:
        for i in tqdm(range(total_chunks), desc="写入 MySQL"):
            start = i * chunksize
            end = min((i + 1) * chunksize, len(result_df))
            chunk = result_df.iloc[start:end]
            chunk.to_sql(table_name, con=conn, index=False, if_exists="replace" if i == 0 else "append")

    print(f"\n新表 `{table_name}` 写入完成，总记录数: {len(result_df)}")


# # 导入数据
# upload()
# 按照lesson_id合并学习记录和学习任务
join()