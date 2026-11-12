import { useEffect } from "react";
import { Platform } from "react-native";
import { useRouter, usePathname } from "expo-router";

export function useTelegramUX() {
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // 📱 네이티브 앱(Android/iOS)에서는 텔레그램 로직이 필요 없으므로 즉시 종료합니다.
    if (Platform.OS !== "web") return;

    const tg = (window as any).Telegram?.WebApp;
    if (!tg) return;

    // 1. 테마(다크모드) 동기화
    tg.ready();
    const bgColor = tg.themeParams?.bg_color || (tg.colorScheme === "dark" ? "#111" : "#fff");
    document.body.style.backgroundColor = bgColor;

    // 2. 뒤로가기 버튼 연동
    const handleBack = () => {
      if (router.canGoBack()) {
        router.back();
      }
    };

    const isRoot = ["/home", "/", "/daily", "/settings", "/compatibility"].includes(pathname);
    
    if (isRoot) {
      tg.BackButton.hide();
    } else {
      tg.BackButton.show();
      tg.BackButton.onClick(handleBack);
    }

    // 클린업 함수
    return () => {
      if (!isRoot) {
        tg.BackButton.offClick(handleBack);
      }
    };
  }, [pathname, router]);
}