import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-col flex-1 items-center justify-center bg-zinc-50 dark:bg-black p-8 text-center">
      <h1 className="text-3xl font-bold mb-4">Legal Trend Radar</h1>
      <p className="max-w-xl text-zinc-600 dark:text-zinc-400 mb-6">
        국가법령정보센터(law.go.kr) 공개 API 기반 계약 관련 판례 검색결과의
        시계열 통계 분석 대시보드입니다. 이 서비스는 <strong>법률 자문이 아니며</strong>,
        소송 결과를 예측하지 않습니다.
      </p>
      <Link
        href="/dashboard"
        className="rounded-full bg-black text-white dark:bg-white dark:text-black px-6 py-3 font-medium"
      >
        대시보드 열기
      </Link>
    </div>
  );
}
