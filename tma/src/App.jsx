import { useEffect, useState } from 'react';
import './App.css';

const CLOUDRUN_URL = 'https://vector-labs-api-787049663118.asia-northeast3.run.app';

export default function App() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('home'); // 'home', 'report', 'daily'

  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    if (tg) {
      tg.ready();
      tg.expand();
    }

    const fetchReport = async () => {
      try {
        const res = await fetch(`${CLOUDRUN_URL}/api/v1/saju/report`, {
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
        console.error(err);
        setError(err.message || 'Network error');
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, []);

  if (loading) return <div className="center-screen"><div className="loader">Aligning your energy...</div></div>;
  if (error) return <div className="center-screen"><div className="error">Failed to load.<br/><small>{error}</small></div></div>;
  if (!report) return <div className="center-screen"><div className="error">No data.</div></div>;

  // --- 데이터 추출 ---
  const luckyCode = report.sections?.lucky_code?.power;
  const luckySignature = luckyCode?.signature || 'GROUND';
  const luckyElementName = luckyCode?.element || 'Earth';
  const sigToFile = { GROWTH: 'wood', SPARK: 'fire', GROUND: 'earth', EDGE: 'metal', FLOW: 'water' };
  const bgKey = sigToFile[luckySignature] || 'earth';
  const wallpaperUrl = `/wallpapers/bg_${bgKey}_generalist.jpg`;
  const elementNameKo = { Wood: '목(木)', Fire: '화(火)', Earth: '토(土)', Metal: '금(金)', Water: '水(水)' }[luckyElementName] || luckyElementName;

  const coreSection = report.sections?.core || {};
  const energySection = report.sections?.energy || {};
  const dailyItems = report.sections?.daily?.items || [];
  const today = dailyItems[0] || {};

  return (
    <div className="app-layout">
      {/* 메인 콘텐츠 영역 */}
      <div className="content-area">
        
        {/* 1. 홈 탭 (배경화면) */}
        {activeTab === 'home' && (
          <div className="tab-page home-page" style={{ backgroundImage: `url(${wallpaperUrl})` }}>
            <div className="glass-overlay">
              <p className="element-tag" style={{ color: '#74b9ff' }}>YOUR CORE ENERGY</p>
              <h1>{elementNameKo} 에너지</h1>
              <p className="tagline">당신의 라이프 블루프린트가 필요로 하는 핵심 에너지입니다.</p>
              <a className="download-btn" href={wallpaperUrl} download={`vectorlabs_core_${bgKey}.jpg`}>📥 내 핵심 에너지 배경화면 저장</a>
            </div>
          </div>
        )}

        {/* 2. 리포트 탭 (본질 & 에너지) */}
        {activeTab === 'report' && (
          <div className="tab-page scroll-page">
            <h2 className="page-title">Your Blueprint</h2>
            <div className="card">
              <h3>{coreSection.archetype?.name || 'Core'}</h3>
              <p className="subtitle">{coreSection.archetype?.tagline}</p>
              {coreSection.narrative?.map((p, i) => <p key={i} className="body-text">{p}</p>)}
            </div>
            <div className="card">
              <h3>Energy Map</h3>
              <p className="subtitle">{energySection.hero}</p>
              {energySection.blocks?.map((b, i) => (
                <div key={i} className="block-item">
                  <strong>{b.name}</strong>
                  <p className="body-text">{b.body}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 3. 일운 탭 (오늘의 운세) */}
        {activeTab === 'daily' && (
          <div className="tab-page scroll-page">
            <h2 className="page-title">Today's Energy</h2>
            {today.name ? (
              <div className="card">
                <div className="daily-header">
                  <span className="badge">{today.grade_label || 'Neutral'}</span>
                  <span className="date">{today.date}</span>
                </div>
                <h3>{today.name}</h3>
                <p className="subtitle">{today.headline}</p>
                {today.body?.split('\n\n').map((p, i) => <p key={i} className="body-text">{p}</p>)}
                <div className="tip-box">
                  <p>💡 <strong>집중:</strong> {today.lean_into}</p>
                  <p>⚠️ <strong>주의:</strong> {today.watch_for}</p>
                </div>
              </div>
            ) : (
              <p>오늘의 운세 데이터가 없습니다.</p>
            )}
          </div>
        )}

      </div>

      {/* 하단 탭 바 */}
      <div className="bottom-tabs">
        <button className={activeTab === 'home' ? 'active' : ''} onClick={() => setActiveTab('home')}>
          <span>🏠</span> Home
        </button>
        <button className={activeTab === 'report' ? 'active' : ''} onClick={() => setActiveTab('report')}>
          <span>📜</span> Report
        </button>
        <button className={activeTab === 'daily' ? 'active' : ''} onClick={() => setActiveTab('daily')}>
          <span>☀️</span> Daily
        </button>
      </div>
    </div>
  );
}