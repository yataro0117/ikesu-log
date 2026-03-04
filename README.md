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

---

## 本番デプロイ（無料構成）

```
フロントエンド: Vercel（無料）
バックエンド:   Render（無料 ※15分無操作でスリープ）
DB:            Supabase（無料・500MB）
```

### Step 1: Supabase でDB作成

1. [supabase.com](https://supabase.com) → **New project** を作成
2. **Project Settings → Database → Connection string** を開く
3. **URI** タブの接続文字列をコピー（形式: `postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres`）
4. この URL はそのまま `DATABASE_URL` に使用できます（`postgresql://` のままでOK。自動変換されます）

### Step 2: バックエンド → Render

1. [render.com](https://render.com) → **New → Web Service**
2. **Connect repository**: `yataro0117/ikesu-log`
3. 以下を設定:

| 項目 | 値 |
|------|----|
| Root Directory | `backend` |
| Runtime | Python |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `alembic upgrade head && python -m app.db.seed && uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

4. **Environment Variables** に追加:

| キー | 値 |
|------|----|
| `DATABASE_URL` | Supabase の接続文字列（postgresql://...） |
| `SECRET_KEY` | ランダム文字列（`openssl rand -hex 32`） |
| `DB_SSL` | `true` |
| `CORS_ORIGINS` | `["https://your-app.vercel.app"]`（後でVercel URLに変更） |

5. **Deploy** → 生成されたURLをメモ（例: `https://ikesu-log-api.onrender.com`）

### Step 3: フロントエンド → Vercel

1. [vercel.com/new](https://vercel.com/new) → **Import** → `yataro0117/ikesu-log`
2. **Root Directory** を **`frontend`** に変更（必須）
3. **Environment Variables**:

| キー | 値 |
|------|----|
| `NEXT_PUBLIC_API_URL` | `https://ikesu-log-api.onrender.com` |

4. **Deploy**

### Step 4: CORS を更新

Vercel の本番 URL（例: `https://ikesu-log.vercel.app`）が確定したら、Render の環境変数を更新:

```
CORS_ORIGINS=["https://ikesu-log.vercel.app"]
```

---

## 画面構成

| タブ | URL | 内容 |
|------|-----|------|
| 今日 | /today | 今日やること・KPIサマリー |
| 生簀 | /cages | 生簀一覧・グリッドマップ |
| 入力 | /input | 生簀選択→クイック入力 |
| 分析 | /analytics | KPI詳細・アラート |
| 出荷 | /harvest | 出荷記録 |

## QR導線

各生簀にQRトークンが割り当て済み。`/qr/{token}` でスキャン→生簀詳細へ自動リダイレクト。

## 環境変数

| 変数 | 説明 |
|------|------|
| `DATABASE_URL` | PostgreSQL接続URL（`postgresql://` or `postgresql+asyncpg://`） |
| `DB_SSL` | `true` にするとSSL強制（Supabase本番用） |
| `SECRET_KEY` | JWT署名キー |
| `CORS_ORIGINS` | 許可オリジン（JSON配列） |
| `NEXT_PUBLIC_API_URL` | フロントからのバックエンドURL |

## 技術スタック

- **Frontend**: Next.js 14 (App Router) + Tailwind CSS + PWA
- **Backend**: FastAPI + SQLAlchemy async + Alembic
- **DB**: PostgreSQL 16 / Supabase
- **認証**: JWT (python-jose + bcrypt)
- **オフライン**: IndexedDB キュー → `/sync/push` で復帰時一括送信
- **開発**: Docker Compose
