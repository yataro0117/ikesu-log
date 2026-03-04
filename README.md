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

## 本番デプロイ（完全無料）

```
フロントエンド: Vercel   （無料・制限なし）
バックエンド:   Render    （無料・15分無操作でスリープ）
DB:            Neon      （無料・512MB・クレジットカード不要）
```

### Step 1: Neon でDB作成（無料PostgreSQL）

1. [neon.tech](https://neon.tech) → **Sign up**（GitHubアカウントでOK）
2. **New Project** → プロジェクト名を入力（例: `ikesu-log`）→ Create
3. ダッシュボードの **Connection Details** → **Connection string** をコピー

```
# コピーされる形式（そのままRenderに貼り付けてOK）
postgresql://username:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

> `?sslmode=require` が付いたままでOKです。自動で除去・SSL設定されます。

### Step 2: バックエンド → Render

1. [render.com](https://render.com) → **New → Web Service**
2. **Connect a repository** → `yataro0117/ikesu-log` を選択
3. 以下を設定:

| 項目 | 値 |
|------|----|
| **Root Directory** | `backend` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `alembic upgrade head && python -m app.db.seed && uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | Free |

4. **Environment Variables** → **Add Environment Variable** で以下を追加:

| キー | 値 |
|------|----|
| `DATABASE_URL` | Neon の接続文字列（`postgresql://...`） |
| `SECRET_KEY` | ランダム文字列（下記参照） |
| `DB_SSL` | `true` |
| `CORS_ORIGINS` | `["https://your-app.vercel.app"]`（後でVercel URLに更新） |

> `SECRET_KEY` の生成: ターミナルで `python3 -c "import secrets; print(secrets.token_hex(32))"` を実行

5. **Create Web Service** → デプロイ完了後にURLをメモ（例: `https://ikesu-log-api.onrender.com`）

### Step 3: フロントエンド → Vercel

1. [vercel.com/new](https://vercel.com/new) → **Import** → `yataro0117/ikesu-log`
2. **Root Directory** を **`frontend`** に変更（必須）
3. **Environment Variables** を追加:

| キー | 値 |
|------|----|
| `NEXT_PUBLIC_API_URL` | Render のURL（例: `https://ikesu-log-api.onrender.com`） |

4. **Deploy**

### Step 4: CORS を更新

Vercel の本番 URL（例: `https://ikesu-log.vercel.app`）が確定したら、
Render の `CORS_ORIGINS` を更新して **Manual Deploy**:

```
CORS_ORIGINS=["https://ikesu-log.vercel.app"]
```

---

## 注意事項

**Render の無料プランのスリープについて**
15分間アクセスがないとバックエンドがスリープします。次のアクセス時に約30秒かかります。
毎朝最初のアクセスだけ遅い、それ以外は通常速度です。

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
| `DATABASE_URL` | PostgreSQL接続URL（`postgresql://` or `postgresql+asyncpg://`。`?sslmode=require`付きもOK） |
| `DB_SSL` | `true` でSSL強制（Neon/Supabase本番用） |
| `SECRET_KEY` | JWT署名キー（本番は32文字以上のランダム文字列） |
| `CORS_ORIGINS` | 許可オリジン（JSON配列） |
| `NEXT_PUBLIC_API_URL` | フロントからのバックエンドURL |

## 技術スタック

- **Frontend**: Next.js 14 (App Router) + Tailwind CSS + PWA
- **Backend**: FastAPI + SQLAlchemy async + Alembic
- **DB**: PostgreSQL 16 / Neon / Supabase
- **認証**: JWT (python-jose + bcrypt)
- **オフライン**: IndexedDB キュー → `/sync/push` で復帰時一括送信
- **開発**: Docker Compose
