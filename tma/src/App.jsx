import { useEffect, useState } from 'react';
import './App.css';

export default function App() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // 텔레그램 SDK 초기화 (없으면 무시)
    const tg = window.Telegram?.WebApp;
    if (tg) {
      try {
        tg.ready();
        tg.expand();
      } catch (e) {
        console.warn('Telegram SDK init failed:', e);
      }
    }

    const fetchReport = async () => {
      try {
        const res = await fetch('/api/v1/saju/report', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            birth_date: "1974-02-24",
            birth_time: "05:30:00",
            birth_location: "seoul",
            gender: "M",
            lang: "ko"
          })
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        setReport(data.report);
      } catch (err) {
        console.error('Report fetch failed:', err);
        setError(err.message || 'Network error');
      } finally {
        setLoading(false);
      }
    };

    // 텔레그램 SDK 로딩 대기 (최대 3초)
    let attempts = 0;
    const checkSdk = setInterval(() => {
      if (window.Telegram?.WebApp || attempts >= 30) {
        clearInterval(checkSdk);
        fetchReport();
      }
      attempts++;
    }, 100);

    return () => clearInterval(checkSdk);
  }, []);

  if (loading) return <div className="center-screen"><div className="loader">Aligning your energy...</div></div>;
  if (error) return <div className="center-screen"><div className="error">Failed to load blueprint.<br /><small>{error}</small></div></div>;
  if (!report) return <div className="center-screen"><div className="error">No data received.</div></div>;

  // ... (이하 기존과 동일: luckyCode 추출 및 렌더링) ...
  const luckyCode = report.sections?.lucky_code?.power;
  const luckySignature = luckyCode?.signature || 'GROUND';
  const luckyElementName = luckyCode?.element || 'Earth';
  const sigToFile = { GROWTH: 'wood', SPARK: 'fire', GROUND: 'earth', EDGE: 'metal', FLOW: 'water' };
  const bgKey = sigToFile[luckySignature] || 'earth';
  const wallpaperUrl = `/wallpapers/bg_${bgKey}_generalist.jpg`;
  const elementNameKo = { Wood: '목(木)', Fire: '화(火)', Earth: '토(土)', Metal: '금(金)', Water: '수(水)' }[luckyElementName] || luckyElementName;

  return (
    <div className="app-container" style={{ backgroundImage: `url(${wallpaperUrl})` }}>
      <div className="glass-overlay">
        <div className="content">
          <p className="element-tag" style={{ color: '#74b9ff' }}>YOUR CORE ENERGY</p>
          <h1>{elementNameKo} 에너지</h1>
          <p className="tagline">당신의 라이프 블루프린트가 필요로 하는 핵심 에너지입니다.<br/>이 시각적 앵커가 매일 당신의 부족한 에너지를 채워줄 것입니다.</p>
          <div className="action-box">
            <a className="download-btn" href={wallpaperUrl} download={`vectorlabs_core_${bgKey}.jpg`}>📥 내 핵심 에너지 배경화면 저장</a>
          </div>
        </div>
      </div>
    </div>
  );
}
