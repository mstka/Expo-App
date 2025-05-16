# auth.py
import os
import jwt
import datetime
from supabase import create_client, Client
from passlib.context import CryptContext

class AuthManager:
    def __init__(self):
        # 環境変数からSupabase設定とJWTシークレットを取得
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.jwt_secret = os.getenv("JWT_SECRET_KEY")
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        # パスワードハッシュ用コンテキスト
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        """プレーンテキストパスワードをハッシュ化"""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """パスワードの照合"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def parse_jwt(self, token: str) -> dict:
        """
        JWTをデコードし、ペイロードを返す。
        有効期限切れ時にはjwt.ExpiredSignatureErrorを投げる。
        """
        return jwt.decode(token, self.jwt_secret, algorithms=["HS256"])

    def issue_jwt(self, user_id: str, expires_delta: datetime.timedelta = None) -> str:
        """
        JWTを発行
        """
        now = datetime.datetime.utcnow()
        exp = now + (expires_delta or datetime.timedelta(hours=1))
        payload = {"sub": user_id, "iat": now, "exp": exp}
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")

    def get_user(self, user_id: str) -> dict:
        """
        SupabaseのUserテーブルからユーザーを取得
        """
        resp = self.supabase.table("User").select("*").eq("userId", user_id).single().execute()
        return resp.data

    def register_user(self, user_id: str, password: str) -> dict:
        """
        新規ユーザーをUserテーブルに登録（パスワードはハッシュ化）
        """
        hashed = self.hash_password(password)
        data = {"userId": user_id, "password": hashed}
        resp = self.supabase.table("User").insert(data).execute()
        return resp.data

    def verify_or_register(self, token: str) -> dict:
        """
        JWTからユーザーIDを取得し、未登録なら新規登録（パスワードなし）
        """
        try:
            payload = self.parse_jwt(token)
            user_id = payload.get("sub")
        except jwt.ExpiredSignatureError:
            return None
        except Exception:
            return None

        user = self.get_user(user_id)
        if not user:
            # パスワードなしのユーザー登録
            user = self.supabase.table("User").insert({"userId": user_id}).execute().data
        return user

    def login(self, user_id: str, password: str) -> str:
        """
        UserテーブルのuserId/passwordで認証し、JWTを返却
        """
        user = self.get_user(user_id)
        if not user:
            raise Exception("ユーザーが存在しません。")
        if not self.verify_password(password, user.get("password", "")):
            raise Exception("パスワードが正しくありません。")
        return self.issue_jwt(user_id)