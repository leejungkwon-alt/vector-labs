// 구매 내역 표시 + 결제 확인 대기 안내용 번역 키를 5개 언어 locale 파일에 추가합니다.
// 사용법 (레포 루트에서):  node scripts/add-purchase-i18n.mjs
// - settings 키: "purchaseHistory" 줄 바로 아래에 삽입
// - payment 키:  "payment": { 줄 바로 아래에 삽입
// - 기존 포맷/줄바꿈(CRLF 포함)을 유지하고, 이미 추가된 섹션은 건너뛰므로 여러 번 실행해도 안전합니다.
// - 결과가 올바른 JSON이 아니거나 키가 의도한 위치에 없으면 파일을 쓰지 않고 중단합니다.
import fs from "node:fs";
import path from "node:path";

const DIR = process.argv[2] ?? "frontend/src/locales";

const T = {
  ko: {
    settings: {
      purchaseSub: "프리미엄 구독",
      purchaseOnetime: "1회 이용권",
      purchaseChannelApp: "앱 결제",
      purchaseChannelWeb: "웹 결제",
      purchaseChannelTelegram: "텔레그램 결제",
      purchaseLabel: "{name}({channel})",
      purchaseViewMore: "더보기 ({count})",
      purchaseCollapse: "접기",
    },
    payment: {
      verifying: "Google 결제를 확인하는 중입니다. 잠시만 기다려 주세요…",
      pendingNotice: "결제가 승인 대기 중입니다. 승인이 끝난 뒤 앱을 다시 열어 확인해 주세요.",
      verifyDelayed: "결제 확인이 지연되고 있습니다. 잠시 후 설정 화면의 구매 내역을 확인해 주세요. 계속 반영되지 않으면 문의해 주세요.",
    },
  },
  en: {
    settings: {
      purchaseSub: "Premium subscription",
      purchaseOnetime: "One-time pass",
      purchaseChannelApp: "App",
      purchaseChannelWeb: "Web",
      purchaseChannelTelegram: "Telegram",
      purchaseLabel: "{name} ({channel})",
      purchaseViewMore: "Show more ({count})",
      purchaseCollapse: "Show less",
    },
    payment: {
      verifying: "Confirming your Google Play payment. This can take a moment…",
      pendingNotice: "Your payment is pending approval. Please reopen the app to check once it's approved.",
      verifyDelayed: "Confirmation is taking longer than expected. Please check Purchase history in Settings in a moment, and contact us if it doesn't appear.",
    },
  },
  ja: {
    settings: {
      purchaseSub: "プレミアム購読",
      purchaseOnetime: "1回利用券",
      purchaseChannelApp: "アプリ決済",
      purchaseChannelWeb: "Web決済",
      purchaseChannelTelegram: "Telegram決済",
      purchaseLabel: "{name}({channel})",
      purchaseViewMore: "もっと見る({count})",
      purchaseCollapse: "閉じる",
    },
    payment: {
      verifying: "Google Playの決済を確認しています。しばらくお待ちください…",
      pendingNotice: "決済は承認待ちです。承認後にアプリを開き直してご確認ください。",
      verifyDelayed: "確認に時間がかかっています。しばらくしてから設定画面の購入履歴をご確認ください。反映されない場合はお問い合わせください。",
    },
  },
  zh_cn: {
    settings: {
      purchaseSub: "高级会员订阅",
      purchaseOnetime: "单次券",
      purchaseChannelApp: "应用内支付",
      purchaseChannelWeb: "网页支付",
      purchaseChannelTelegram: "Telegram支付",
      purchaseLabel: "{name}({channel})",
      purchaseViewMore: "查看更多({count})",
      purchaseCollapse: "收起",
    },
    payment: {
      verifying: "正在确认 Google Play 付款，请稍候…",
      pendingNotice: "付款正在等待批准，批准后请重新打开应用查看。",
      verifyDelayed: "确认耗时较长。请稍后在设置中查看购买记录，如仍未显示请联系我们。",
    },
  },
  es: {
    settings: {
      purchaseSub: "Suscripción Premium",
      purchaseOnetime: "Pase único",
      purchaseChannelApp: "App",
      purchaseChannelWeb: "Web",
      purchaseChannelTelegram: "Telegram",
      purchaseLabel: "{name} ({channel})",
      purchaseViewMore: "Ver más ({count})",
      purchaseCollapse: "Ver menos",
    },
    payment: {
      verifying: "Confirmando tu pago de Google Play. Puede tardar un momento…",
      pendingNotice: "Tu pago está pendiente de aprobación. Vuelve a abrir la app para comprobarlo cuando se apruebe.",
      verifyDelayed: "La confirmación está tardando más de lo esperado. Revisa el historial de compras en Ajustes en unos minutos y contáctanos si no aparece.",
    },
  },
};

// 섹션별 삽입 위치와 "이미 추가됨" 판정 키
const SECTIONS = {
  settings: { anchor: /^\s*"purchaseHistory"\s*:/, afterOpening: false, marker: "purchaseLabel" },
  payment: { anchor: /^\s*"payment"\s*:\s*\{\s*$/, afterOpening: true, marker: "verifyDelayed" },
};

let failed = false;
for (const [lang, sections] of Object.entries(T)) {
  const file = path.join(DIR, `${lang}.json`);
  let raw = fs.readFileSync(file, "utf8");
  const eol = raw.includes("\r\n") ? "\r\n" : "\n";
  let lines = raw.split(/\r?\n/);
  let changed = 0;

  for (const [name, entries] of Object.entries(sections)) {
    const sec = SECTIONS[name];
    if (lines.some((l) => l.includes(`"${sec.marker}"`))) {
      console.log(`${lang}.${name}: 이미 추가됨 — 건너뜀`);
      continue;
    }
    const idx = lines.reduce((acc, l, i) => (sec.anchor.test(l) ? [...acc, i] : acc), []);
    if (idx.length !== 1) {
      console.error(`${lang}.${name}: 삽입 위치를 정확히 1곳 찾지 못함 (${idx.length}곳) — 중단`);
      failed = true;
      continue;
    }
    const i = idx[0];
    if (!sec.afterOpening && !lines[i].trimEnd().endsWith(",")) {
      console.error(`${lang}.${name}: 기준 줄 끝에 쉼표가 없음 — 중단 (수동 확인 필요)`);
      failed = true;
      continue;
    }
    // 들여쓰기: 여는 줄이면 다음 줄 기준, 아니면 기준 줄 기준
    const indent = (sec.afterOpening ? lines[i + 1] ?? lines[i] : lines[i]).match(/^\s*/)[0];
    const added = Object.entries(entries).map(([k, v]) => `${indent}${JSON.stringify(k)}: ${JSON.stringify(v)},`);
    const next = [...lines.slice(0, i + 1), ...added, ...lines.slice(i + 1)];

    try {
      const parsed = JSON.parse(next.join(eol));
      const first = Object.keys(entries)[0];
      if (parsed?.[name]?.[first] !== entries[first]) throw new Error(`${name} 아래에 들어가지 않음`);
    } catch (e) {
      console.error(`${lang}.${name}: 결과 검증 실패 (${e.message}) — 쓰지 않음`);
      failed = true;
      continue;
    }
    lines = next;
    changed += added.length;
    console.log(`${lang}.${name}: 키 ${added.length}개 추가`);
  }

  if (changed > 0) fs.writeFileSync(file, lines.join(eol), "utf8");
}
process.exit(failed ? 1 : 0);
