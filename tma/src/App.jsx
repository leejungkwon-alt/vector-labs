import { useEffect, useState } from 'react';
import './App.css';

const CLOUDRUN_URL = 'https://vector-labs-api-787049663118.asia-northeast3.run.app';

// --- 1. 온보딩(정보 입력) 컴포넌트 ---
function OnboardingScreen({ onComplete }) {
  const [birthDate, setBirthDate] = useState('1990-01-01');
  const [birthTime, setBirthTime] = useState('12:00');
  const [gender, setGender] = useState('M');
  const [location, setLocation] = useState('seoul');

  const handleSubmit = (e) => {
    e.preventDefault();
    const profile = {
      birth_date: birthDate,
      birth_time: birthTime + ':00',
      birth_time_mode: 'exact',
      birth_location: location,
      gender: gender,
      lang: 'ko',
    };
    onComplete(profile);
  };

  return (
    <div className="onboarding-container">
      <div className="onboarding-card">
        <h1>Welcome to Vector Labs</h1>
        <p>당신만의 라이프 블루프린트를 찾기 위해<br/>출생 정보를 입력해 주세요.</p>
        
        <form onSubmit={handleSubmit} className="onboarding-form">
          <label>
            생년월일
            <input type="date" value={birthDate} onChange={(e) => setBirthDate(e.target.value)} required />
          </label>
          <label>
            출생 시간 (모르면 12:00)
            <input type="time" value={birthTime} onChange={(e) => setBirthTime(e.target.value)} required />
          </label>
          <label>
            성별
            <select value={gender} onChange={(e) => setGender(e.target.value)}>
              <option value="M">남성</option>
              <option value="F">여성</option>
            </select>
          </label>
          <label>
            출생지
            <select value={location} onChange={(e) => setLocation(e.target.value)}>
              <option value="seoul">서울</option>
              <option value="busan">부산</option>
              <option value="new_york">뉴욕</option>
              <option value="tokyo">도쿄</option>
            </select>
          </label>
          <button type="submit" className="start-btn">내 블루프린트 생성하기</button>
        </form>
      </div>
    </div>
  );
}

// --- 2. 메인 앱 컴포넌트 ---
export default function App() {
  const [profile, setProfile] = useState(null);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('home');

  // 초기 로드 시 로컬 스토리지 확인
  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    if (tg) {
      tg.ready();
      tg.expand();
    }
    const saved = localStorage.getItem('saju_profile');
    if (saved) {
      setProfile(JSON.parse(saved));
    }
  }, []);

  // 프로필이 설정되면 리포트 가져오기
  useEffect(() => {
    if (!profile) return;
    
    setLoading(true);
    setError(null);
    
    const fetchReport = async () => {
      try {
        const res = await fetch(`${CLOUDRUN_URL}/api/v1/saju/report`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(profile)
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
  }, [profile]);

  const handleOnboardingComplete = (newProfile) => {
    localStorage.setItem('saju_profile', JSON.stringify(newProfile));
    setProfile(newProfile);
  };

  // --- 렌더링 분기 ---
  if (!profile) {
    return <OnboardingScreen onComplete={handleOnboardingComplete} />;
  }

  if (loading) {
    return <div className="center-screen"><div className="loader">우주의 기운을 계산하고 있어요...</div></div>;
  }

  if (error || !report) {
    return (
      <div className="center-screen">
        <div className="error">Failed to load.<br/><small>{error}</small></div>
        <button onClick={() => { localStorage.removeItem('saju_profile'); setProfile(null); }} className="reset-btn">다시 입력하기</button>
      </div>
    );
  }

  // --- 데이터 추출 ---
  const luckyCode = report.sections?.lucky_code?.power;
  const luckySignature = luckyCode?.signature || 'GROUND';
  const luckyElementName = luckyCode?.element || 'Earth';
  const sigToFile = { GROWTH: 'wood', SPARK: 'fire', GROUND: 'earth', EDGE: 'metal', FLOW: 'water' };
  const bgKey = sigToFile[luckySignature] || 'earth';
  const wallpaperUrl = `/wallpapers/bg_${bgKey}_generalist.jpg`;
  const elementNameKo = { Wood: '목(木)', Fire: '화(火)', Earth: '토(土)', Metal: '금(金)', Water: '수(水)' }[luckyElementName] || luckyElementName;

  const coreSection = report.sections?.core || {};
  const energySection = report.sections?.energy || {};
  const dailyItems = report.sections?.daily?.items || [];
  const today = dailyItems[0] || {};

  return (
    <div className="app-layout">
      <div className="content-area">
        
        {/* 탭 1: 홈 */}
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

        {/* 탭 2: 리포트 */}
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

        {/* 탭 3: 일운 */}
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