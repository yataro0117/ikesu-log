# いけすログ (Ikesu Log)

養殖生産管理PWAアプリ。カンパチ・ハマチ・ブリ・モジャコの生簀管理を現場で即使える形に。

## クイックスタート

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
./init.sh migrate     # Alembicマイグレーション
./init.sh seed        # シードデータ投入
./init.sh test        # バックエンドテスト実行
./init.sh psql        # PostgreSQL接続
./init.sh shell-be    # バックエンドshell
```

## 画面構成

| タブ | URL | 内容 |
|------|-----|------|
| 今日 | /today | 今日やること・KPIサマリー |
| 生簀 | /cages | 生簀一覧・マップ |
| 入力 | /input | 生簀選択→クイック入力 |
| 分析 | /analytics | KPI詳細・アラート |
| 出荷 | /harvest | 出荷記録 |

## QR導線

各生簀にQRトークンが割り当て済み。
`/qr/{token}` にアクセスすると自動で生簀詳細ページへリダイレクト。
QRコード画像: `GET /cages/{id}/qr`

## Vercelデプロイ

### フロントエンド (Vercel)

```bash
cd frontend
vercel --prod
# 環境変数: NEXT_PUBLIC_API_URL=https://your-backend-url
```

### バックエンド (Railway / Render 等)

```bash
cd backend
# DATABASE_URL, SECRET_KEY などを環境変数に設定
# uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## 環境変数

| 変数 | 説明 |
|------|------|
| DATABASE_URL | PostgreSQL接続URL (asyncpg) |
| SECRET_KEY | JWT署名キー |
| CORS_ORIGINS | 許可オリジン (JSON配列) |
| NEXT_PUBLIC_API_URL | フロントからのAPI URL |

## 技術スタック

- **Frontend**: Next.js 14 (App Router) + Tailwind CSS + shadcn/ui + PWA
- **Backend**: FastAPI + SQLAlchemy (async) + Alembic
- **DB**: PostgreSQL 16
- **認証**: JWT (python-jose)
- **オフライン**: IndexedDB キュー → オンライン復帰時に同期

## DBスキーマ

`backend/alembic/versions/0001_initial.py` 参照
