"use client";
import { useEffect, useState } from "react";

export default function ThemeToggle() {
  const [dark, setDark] = useState(false);

  useEffect(() => {
    setDark(document.documentElement.classList.contains("dark"));
  }, []);

  function toggle() {
    const next = !dark;
    setDark(next);
    document.documentElement.classList.toggle("dark", next);
    try {
      localStorage.setItem("theme", next ? "dark" : "light");
    } catch {
      // localStorage may be unavailable (private mode) - toggle still works for this session.
    }
  }

  return (
    <button
      type="button"
      onClick={toggle}
      aria-label="다크 모드 전환"
      className="rounded-md border border-gray-300 dark:border-gray-600 px-3 py-1.5 text-sm
                 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200
                 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
    >
      {dark ? "☀️ 라이트 모드" : "🌙 다크 모드"}
    </button>
  );
}
