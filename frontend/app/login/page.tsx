"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { login } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("admin@ikesu.local");
  const [password, setPassword] = useState("admin1234");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await login(email, password);
      router.replace("/today");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "ログインに失敗しました");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-ocean-900 to-ocean-700 px-4">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">🐟</div>
          <h1 className="text-3xl font-bold text-white tracking-tight">いけすログ</h1>
          <p className="text-ocean-200 text-sm mt-1">養殖生産管理システム</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-white rounded-2xl p-6 shadow-xl">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-ocean-800 mb-1">
                メールアドレス
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full border border-ocean-200 rounded-xl px-4 py-3 text-ocean-900 focus:outline-none focus:ring-2 focus:ring-ocean-500 bg-ocean-50"
                placeholder="admin@ikesu.local"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-ocean-800 mb-1">
                パスワード
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full border border-ocean-200 rounded-xl px-4 py-3 text-ocean-900 focus:outline-none focus:ring-2 focus:ring-ocean-500 bg-ocean-50"
                placeholder="••••••••"
                required
              />
            </div>
            {error && (
              <p className="text-red-600 text-sm bg-red-50 rounded-lg px-3 py-2">{error}</p>
            )}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-ocean-600 hover:bg-ocean-700 text-white font-semibold py-3 rounded-xl transition-colors disabled:opacity-50 text-base"
            >
              {loading ? "ログイン中..." : "ログイン"}
            </button>
          </div>
          <p className="text-center text-xs text-ocean-400 mt-4">
            デモ: admin@ikesu.local / admin1234
          </p>
        </form>
      </div>
    </div>
  );
}
