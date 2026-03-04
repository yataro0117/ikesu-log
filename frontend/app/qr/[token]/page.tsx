"use client";
import { useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { api } from "@/lib/api";

export default function QRRedirectPage() {
  const { token } = useParams<{ token: string }>();
  const router = useRouter();

  useEffect(() => {
    api.cageQr(token)
      .then((data) => {
        router.replace(`/cages/${data.cage_id}`);
      })
      .catch(() => {
        router.replace("/cages");
      });
  }, [token, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-ocean-50">
      <div className="text-center">
        <div className="text-4xl mb-4">📷</div>
        <p className="text-ocean-600">QRコードを確認中...</p>
      </div>
    </div>
  );
}
