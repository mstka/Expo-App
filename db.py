from supabase import create_client, Client
import requests

class SupabaseDB:
    """
    SupabaseDB は Supabase で管理されている PostgreSQL データベースに対して
    基本的な操作を行うクラスです。

    メソッド:
        - execute_sql: 生の SQL 文を実行します（Supabase プロジェクトで pg_execute_sql が有効な場合）。
        - add_column: テーブルに列を追加します。
        - insert: レコードを挿入します。
        - select: 条件を指定してレコードを取得します。
        - update: 条件に一致するレコードを更新します。
        - delete: 条件に一致するレコードを削除します。
    """

    def __init__(self, url: str, key: str):
        # Supabase の URL と API キーを受け取り、クライアントを初期化する
        self.url = url
        self.key = key
        self.client: Client = create_client(url, key)
        # REST API 呼び出し用のヘッダー
        self.headers = {
            'apikey': key,
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json'
        }

    def execute_sql(self, sql: str):
        """
        生の SQL 文を Supabase の SQL エンドポイント経由で実行します。
        pg_execute_sql 拡張が有効になっている必要があります。

        :param sql: 実行する SQL 文
        :return: 実行結果の JSON レスポンス
        """
        payload = {'sql': sql}
        resp = requests.post(f"{self.url}/rest/v1/rpc/exec_sql", headers=self.headers, json=payload)
        resp.raise_for_status()
        return resp.json()

    def add_column(self, table: str, column_name: str, column_type: str, is_nullable: bool = True, default: str = None):
        """
        テーブルに列を追加します（存在しない場合のみ）。

        :param table: 対象のテーブル名
        :param column_name: 追加する列名
        :param column_type: データ型（例: TEXT, INTEGER）
        :param is_nullable: NULL 許可可否（デフォルト: True）
        :param default: デフォルト値（SQL 表現として文字列で指定）
        :return: SQL 実行結果
        """
        sql = f'ALTER TABLE "{table}" ADD COLUMN IF NOT EXISTS {column_name} {column_type}'
        if default is not None:
            sql += f' DEFAULT {default}'
        if not is_nullable:
            sql += ' NOT NULL'
        return self.execute_sql(sql)

    def insert(self, table: str, data: dict):
        """
        レコードをテーブルに挿入します。

        :param table: 対象のテーブル名
        :param data: 挿入するデータ（列名: 値 の dict）
        :return: 挿入結果
        """
        return self.client.table(table).insert(data).execute()

    def select(self, table: str, columns: str = '*', filters: dict = None):
        """
        テーブルからレコードを取得します。

        :param table: 対象のテーブル名
        :param columns: 取得する列（カンマ区切り文字列または '*'）
        :param filters: 条件指定（列名: 値 の dict）
        :return: 取得結果
        """
        query = self.client.table(table).select(columns)
        if filters:
            for col, val in filters.items():
                query = query.eq(col, val)
        return query.execute()

    def update(self, table: str, data: dict, filters: dict):
        """
        テーブルのレコードを更新します。

        :param table: 対象のテーブル名
        :param data: 更新内容（列名: 新しい値 の dict）
        :param filters: 更新対象の条件指定（列名: 値 の dict）
        :return: 更新結果
        """
        query = self.client.table(table).update(data)
        for col, val in filters.items():
            query = query.eq(col, val)
        return query.execute()

    def delete(self, table: str, filters: dict):
        """
        テーブルからレコードを削除します。

        :param table: 対象のテーブル名
        :param filters: 削除対象の条件指定（列名: 値 の dict）
        :return: 削除結果
        """
        query = self.client.table(table).delete()
        for col, val in filters.items():
            query = query.eq(col, val)
        return query.execute()

# --- 使用例 ---
# from supabase_db_module import SupabaseDB
# db = SupabaseDB("https://xyzcompany.supabase.co", "public-anon-key")
# db.add_column("users", "age", "INTEGER", is_nullable=False, default="0")
# db.insert("users", {"id": 1, "name": "Alice"})
# resp = db.select("users", filters={"id": 1})
# db.update("users", {"name": "Bob"}, filters={"id": 1})
# db.delete("users", filters={"id": 1})
