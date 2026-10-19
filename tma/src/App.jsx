import { useEffect, useState } from 'react';
import './App.css';

export default function App() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    if (tg) {
      tg.ready();
      tg.expand();
    }

    const fetchReport = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/v1/saju/report', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            birth_date: "1974-02-24",
            birth_time: "05:30:00",
            birth_location: "seoul",
            gender: "M",
            lang: "ko" // 나중에 글로벌 유저를 위해 "en"으로 확장 가능
          })
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        setReport(data.report);
      } catch (err) {
        console.error(err);
        setError(err.message || 'An unknown error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, []);

  if (loading) {
    return <div className="center-screen"><div className="loader">Aligning your energy...</div></div>;
  }

  if (error || !report) {
    return <div className="center-screen"><div className="error">Failed to load blueprint.<br /><small>{error}</small></div></div>;
  }

  // 필요한 기운(용신) 추출
  const luckyCode = report.sections?.lucky_code?.power;
  const luckySignature = luckyCode?.signature || 'GROUND'; 
  const luckyElementName = luckyCode?.element || 'Earth'; // Wood, Fire, Earth, Metal, Water
  
  // 파일명 매핑 (GROWTH -> wood)
  const sigToFile = {
    GROWTH: 'wood',
    SPARK: 'fire',
    GROUND: 'earth',
    EDGE: 'metal',
    FLOW: 'water'
  };
  const bgKey = sigToFile[luckySignature] || 'earth';
  const wallpaperUrl = `/wallpapers/bg_${bgKey}_generalist.jpg`;

  // 한글/영어 다국어 처리용 (지금은 한글로, 나중에 en으로 변경)
  const elementNameKo = {
    Wood: '목(木)', Fire: '화(火)', Earth: '토(土)', Metal: '금(金)', Water: '수(水)'
  }[luckyElementName] || luckyElementName;

  return (
    <div
      className="app-container"
      style={{ backgroundImage: `url(${wallpaperUrl})` }}
    >
      <div className="glass-overlay">
        <div className="content">
          {/* '사주' 대신 'Core Energy' 사용 */}
          <p className="element-tag" style={{ color: '#74b9ff' }}>
            YOUR CORE ENERGY
          </p>
          
          <h1>{elementNameKo} 에너지</h1>
          <p className="tagline">
            당신의 <strong>라이프 블루프린트(Life Blueprint)</strong>가 필요로 하는 핵심 에너지입니다.<br/>
            이 시각적 앵커가 매일 당신의 부족한 에너지를 채워줄 것입니다.
          </p>

          <div className="action-box">
            <a
              className="download-btn"
              href={wallpaperUrl}
              download={`vectorlabs_core_${bgKey}.jpg`}
            >
              📥 내 핵심 에너지 배경화면 저장
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}