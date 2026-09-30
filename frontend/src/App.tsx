import { useEffect, useState } from 'react'

type Health = { status: string; db: { status: string; pgvector?: string | null } }

// 개발환경 연결 확인용 화면. 채팅 UI로 교체 예정.
export default function App() {
  const [health, setHealth] = useState<Health | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('/api/health')
      .then((r) => r.json())
      .then(setHealth)
      .catch((e) => setError(String(e)))
  }, [])

  return (
    <main style={{ fontFamily: 'system-ui, sans-serif', padding: 24 }}>
      <h1>악취 근거기반 자동응답 (개발 환경)</h1>
      {error && <p>백엔드 연결 실패: {error}</p>}
      {!health && !error && <p>백엔드 확인 중…</p>}
      {health && <pre>{JSON.stringify(health, null, 2)}</pre>}
    </main>
  )
}
