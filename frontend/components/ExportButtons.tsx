import { exportUrl } from "@/lib/api";

export default function ExportButtons() {
  return (
    <div className="flex gap-2">
      <a
        href={exportUrl("csv")}
        className="rounded-md border border-gray-300 dark:border-gray-600 px-3 py-1.5 text-sm
                   bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200
                   hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
      >
        ⬇ CSV 다운로드
      </a>
      <a
        href={exportUrl("json")}
        className="rounded-md border border-gray-300 dark:border-gray-600 px-3 py-1.5 text-sm
                   bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200
                   hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
      >
        ⬇ JSON 다운로드
      </a>
    </div>
  );
}
