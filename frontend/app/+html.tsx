import { ScrollViewStyleReset } from 'expo-router/html';
import { type PropsWithChildren } from 'react';

export default function Root({ children }: PropsWithChildren) {
  return (
    <html lang="ko">
      <head>
        <meta charSet="utf-8" />
        <meta httpEquiv="X-UA-Compatible" content="IE=edge" />
        <meta
          name="viewport"
          content="width=device-width, initial-scale=1, shrink-to-fit=no, viewport-fit=cover"
        />
        <script src="https://telegram.org/js/telegram-web-app.js"></script>

        {/* 스플래시용 붓글씨체: '결' 한 글자만 내려받는다(text=%EA%B2%B0). display=block 으로 글꼴 로드 전 깜빡임 방지 */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css?family=Nanum+Brush+Script&text=%EA%B2%B0&display=block"
        />

        <ScrollViewStyleReset />
        <style dangerouslySetInnerHTML={{ __html: `
          html, body { height: 100%; margin: 0; padding: 0; overflow: hidden; }
          #root {
            margin: 0; padding: 0; overflow: hidden;
            height: 100vh;
            height: 100dvh;
            height: var(--tg-viewport-stable-height, 100dvh);
          }
        `}} />
      </head>
      <body>{children}</body>
    </html>
  );
}
