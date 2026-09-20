# Legal Trend Radar - Frontend

Next.js (App Router) + TypeScript + Tailwind + Recharts 대시보드입니다.
`NEXT_PUBLIC_API_URL`을 통해 **오직** FastAPI 백엔드하고만 통신하며,
law.go.kr을 직접 호출하지 않습니다.

```powershell
cd frontend
npm install
copy .env.local.example .env.local
npm run dev
```

http://localhost:3000 을 연 뒤 http://localhost:3000/dashboard 로 이동하세요.

전체 프로젝트 개요, 법률 고지문, 파이프라인 실행 방법은 레포 루트의
README를 참고하세요.
