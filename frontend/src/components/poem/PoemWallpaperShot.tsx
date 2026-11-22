// 앱(Android/iOS)에서 "시조 배경화면"을 이미지로 캡처하기 위한 화면 구성.
// 웹의 canvas 합성(PoemFlipCard.handleSaveWallpaper)과 같은 모양을 React Native 뷰로 그린다.
// - 배경 이미지 위에 아래쪽 어두운 그라데이션, 제목, 한글 시조, (한국어일 때) 로마자, 오른쪽 아래 QR
// - QR은 qrcode 패키지의 순수 JS 코어만 사용한다 (canvas/document 불필요 → 앱에서 안전)
import React, { forwardRef, useMemo } from "react";
import { View, Text, Image, StyleSheet } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import Svg, { Rect, Path } from "react-native-svg";

export const SITE_URL = "https://gyeol-blond.vercel.app";

function QrSvg({ value, size }: { value: string; size: number }) {
  const { n, d } = useMemo(() => {
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const core = require("qrcode/lib/core/qrcode");
    const qr = core.create(value, { errorCorrectionLevel: "M" });
    const n: number = qr.modules.size;
    const data: ArrayLike<number> = qr.modules.data;
    let d = "";
    for (let r = 0; r < n; r++) {
      for (let c = 0; c < n; c++) {
        if (data[r * n + c]) d += `M${c} ${r}h1v1h-1z`;
      }
    }
    return { n, d };
  }, [value]);

  const quiet = 2; // QR 규격상 필요한 흰 여백(모듈 2칸)
  const full = n + quiet * 2;
  return (
    <Svg width={size} height={size} viewBox={`${-quiet} ${-quiet} ${full} ${full}`}>
      <Rect x={-quiet} y={-quiet} width={full} height={full} fill="#ffffff" />
      <Path d={d} fill="#1a1a1a" />
    </Svg>
  );
}

type Props = {
  imageUri: string;
  width: number;
  height: number;
  title: string;
  sijo: string;
  romanization?: string; // 한국어일 때만 전달
  onImageLoad?: () => void;
  onImageError?: () => void;
};

// ref는 view-shot의 captureRef에 넘길 루트 View를 가리킨다 (RN 버전별 View 타입 차이를 피하려고 any)
export const PoemWallpaperShot = forwardRef<any, Props>(function PoemWallpaperShot(
  { imageUri, width: W, height: H, title, sijo, romanization, onImageLoad, onImageError },
  ref
) {
  const titleSize = Math.round(W * 0.07);
  const sijoSize = Math.round(W * 0.05);
  const romanSize = Math.max(8, Math.round(W * 0.025));
  const qrSize = Math.round(W * 0.12);
  const overlayH = Math.round(H * 0.5);
  const lines = (sijo || "").split(/\n/).map((s) => s.trim()).filter(Boolean);

  return (
    <View ref={ref} collapsable={false} style={[styles.root, { width: W, height: H }]}>
      <Image
        source={{ uri: imageUri }}
        style={StyleSheet.absoluteFill}
        resizeMode="cover"
        onLoad={onImageLoad}
        onError={onImageError}
      />

      <LinearGradient
        colors={["rgba(0,0,0,0)", "rgba(0,0,0,0.55)", "rgba(0,0,0,0.82)"]}
        locations={[0, 0.4, 1]}
        pointerEvents="none"
        style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: overlayH }}
      />

      <View
        pointerEvents="none"
        style={{
          position: "absolute", left: 0, right: 0, bottom: 0, height: overlayH,
          paddingTop: Math.round(titleSize * 0.65), paddingHorizontal: Math.round(W * 0.06),
          alignItems: "center",
        }}
      >
        <Text style={[styles.shadow, { fontSize: titleSize, fontWeight: "700", color: "rgba(255,255,255,0.98)", textAlign: "center" }]}>
          {title}
        </Text>
        <View style={{ marginTop: Math.round(sijoSize * 0.9), alignItems: "center" }}>
          {lines.map((line, i) => (
            <Text
              key={i}
              style={[styles.shadow, { fontSize: sijoSize, lineHeight: Math.round(sijoSize * 1.6), color: "rgba(240,245,255,0.95)", textAlign: "center" }]}
            >
              {line}
            </Text>
          ))}
        </View>
        {romanization ? (
          <Text
            style={[styles.shadow, { marginTop: Math.round(romanSize * 1.2), fontSize: romanSize, fontStyle: "italic", color: "rgba(200,220,255,0.7)", textAlign: "center", maxWidth: W * 0.7 }]}
          >
            {romanization}
          </Text>
        ) : null}
      </View>

      <View
        pointerEvents="none"
        style={{ position: "absolute", right: Math.round(W * 0.04), bottom: Math.round(W * 0.015), alignItems: "center" }}
      >
        <QrSvg value={SITE_URL} size={qrSize} />
        <Text style={{ marginTop: Math.round(W * 0.008), fontSize: Math.max(7, Math.round(W * 0.02)), fontStyle: "italic", color: "rgba(255,255,255,0.75)" }}>
          gyeol.app
        </Text>
      </View>
    </View>
  );
});

const styles = StyleSheet.create({
  root: { backgroundColor: "#000", overflow: "hidden" },
  shadow: { textShadowColor: "rgba(0,0,0,0.8)", textShadowOffset: { width: 0, height: 1 }, textShadowRadius: 6 },
});
