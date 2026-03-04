# いけすログ (Ikesu Log)

養殖生産管理PWAアプリ。カンパチ・ハマチ・ブリ・モジャコの生簀管理を現場で即使える形に。

## クイックスタート（ローカル）

```bash
cp .env.example .env
./init.sh up
```

- **フロントエンド**: http://localhost:3000
- **バックエンドAPI**: http://localhost:8000/docs

### 初期ログイン

| ロール | メール | パスワード |
|--------|--------|------------|
| 管理者 | admin@ikesu.local | admin1234 |
| 現場 | worker@ikesu.local | worker1234 |

## init.sh コマンド

```bash
./init.sh up          # 起動 (ビルド + マイグレーション + seed)
./init.sh down        # 停止
./init.sh logs        # ログ確認
./init.sh test        # バックエンドテスト実行
./init.sh psql        # PostgreSQL接続
./init.sh seed        # シードデータ再投入
```

## 本番デプロイ

### 1. バックエンド → Railway

1. [railway.app](https://railway.app) でNew Project → Deploy from GitHub repo
2. Root Directory: `backend`
3. 環境変数を設定（下表参照）
4. PostgreSQL プラグインを追加 → `DATABASE_URL` が自動設定される

```
SECRET_KEY=<ランダム長文字列>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=["https://your-app.vercel.app"]
```

### 2. フロントエンド → Vercel

1. [vercel.com](https://vercel.com) でImport → このリポジトリを選択
2. **Root Directory: `frontend`** に設定（重要）
3. 環境変数を設定:

```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

4. Deploy ボタンを押す

## 画面構成

| タブ | URL | 内容 |
|------|-----|------|
| 今日 | /today | 今日やること・KPIサマリー |
| 生簀 | /cages | 生簀一覧・グリッドマップ |
| 入力 | /input | 生簀選択→クイック入力 |
| 分析 | /analytics | KPI詳細・アラート |
| 出荷 | /harvest | 出荷記録 |

## QR導線

各生簀にQRトークンが割り当て済み。
`/qr/{token}` にアクセスすると自動で生簀詳細ページへリダイレクト。
QRコード画像: `GET /cages/{id}/qr`（認証必要）

## 環境変数

### バックエンド

| 変数 | 説明 |
|------|------|
| `DATABASE_URL` | PostgreSQL接続URL（asyncpg形式）|
| `SECRET_KEY` | JWT署名キー（本番は長いランダム文字列）|
| `CORS_ORIGINS` | 許可オリジン（JSON配列）|

### フロントエンド

| 変数 | 説明 |
|------|------|
| `NEXT_PUBLIC_API_URL` | バックエンドのURL |

## 技術スタック

- **Frontend**: Next.js 14 (App Router) + Tailwind CSS + PWA (next-pwa)
- **Backend**: FastAPI + SQLAlchemy async + Alembic
- **DB**: PostgreSQL 16
- **認証**: JWT (python-jose + bcrypt)
- **オフライン**: IndexedDB キュー → `/sync/push` で復帰時一括送信
- **開発**: Docker Compose

## DBスキーマ

`backend/alembic/versions/0001_initial.py` 参照

## テスト実行

```bash
./init.sh test
# → 16件全通過（API統合テスト + KPI計算ユニットテスト）
```
