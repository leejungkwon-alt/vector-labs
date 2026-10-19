import { useEffect, useState } from 'react';
import './App.css';

const API_BASE = 'https://vector-labs-api-787049663118.asia-northeast3.run.app/api/v1';

// --- 공통 컴포넌트 ---
function Accordion({ title, isOpen, onToggle, children, isLocked }) {
  return (
    <div className="accordion">
      <button className="acc-header" onClick={onToggle}>
        <span>{title}</span>
        <span>{isOpen ? '−' : '+'}</span>
      </button>
      {isOpen && (
        <div className="acc-content">
          {children}
          {isLocked && (
            <div className="locked-box">
              <span>🔒</span> 더 깊은 분석은 프리미엄에서 확인하세요.
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// --- 탭 1: 온보딩 ---
function Onboarding({ onSubmit }) {
  const [bd, setBd] = useState('1995-05-05');
  const [bt, setBt] = useState('12:00');
  const [gender, setGender] = useState('M');
  const [loc, setLoc] = useState('seoul');

  return (
    <div className="onboarding">
      <div className="onboarding-card">
        <h1>Vector Labs</h1>
        <p>당신의 라이프 블루프린트를 찾기 위해<br/>출생 정보를 입력해 주세요.</p>
        <form onSubmit={(e) => { e.preventDefault(); onSubmit({ birth_date: bd, birth_time: bt + ':00', birth_location: loc, gender, lang: 'ko' }); }}>
          <label>생년월일 <input type="date" value={bd} onChange={e => setBd(e.target.value)} required /></label>
          <label>출생 시간 <input type="time" value={bt} onChange={e => setBt(e.target.value)} required /></label>
          <label>성별
            <select value={gender} onChange={e => setGender(e.target.value)}>
              <option value="M">남성</option><option value="F">여성</option>
            </select>
          </label>
          <label>출생지
            <select value={loc} onChange={e => setLoc(e.target.value)}>
              <option value="seoul">서울</option><option value="busan">부산</option>
              <option value="new_york">뉴욕</option><option value="tokyo">도쿄</option>
            </select>
          </label>
          <button type="submit" className="primary-btn">블루프린트 생성</button>
        </form>
      </div>
    </div>
  );
}

// --- 탭 2: 홈 (리포트 뷰어) ---
function HomeTab({ report, expanded, toggle }) {
  const s = report.sections || {};
  const renderContent = (key, sec) => {
    switch (key) {
      case 'chart':
        return sec.layers?.map((l, i) => <div key={i} className="item"><strong>{l.label} ({l.archetype})</strong><p>{l.narrative}</p></div>);
      case 'core':
        return <div>{sec.narrative?.map((p, i) => <p key={i}>{p}</p>)}</div>;
      case 'energy':
        return sec.blocks?.map((b, i) => <div key={i} className="item"><strong>{b.name}</strong><p>{b.body}</p></div>);
      case 'lucky_code':
        return <div><p>• 핵심 기운: {sec.power?.element}</p><p>• 추천 색상: {sec.power?.colors?.join(', ')}</p></div>;
      case 'health':
        return sec.blocks?.map((b, i) => <div key={i} className="item"><strong>{b.name}</strong><p>{b.body}</p></div>);
      case 'money':
      case 'work':
      case 'bonds':
        return <div><h4>{sec.headline}</h4><p>{sec.body}</p></div>;
      case 'timeline':
        return sec.items?.map((i, idx) => <div key={idx} className="item-row"><span>{i.ages[0]}~{i.ages[1]}세 ({i.pillar})</span><strong>{i.grade}</strong></div>);
      case 'monthly':
        return sec.items?.map((i, idx) => <div key={idx} className="item"><strong>{i.approx_solar_month} ({i.pillar})</strong><p>{i.headline}</p></div>);
      default:
        return <p className="text-muted">콘텐츠 준비 중입니다.</p>;
    }
  };

  return (
    <div className="tab-pane">
      <div className="cover" style={{ backgroundImage: `url(${report.meta?.daily_wallpaper_url || ''})` }}>
        <h1>{report.cover?.archetype?.name}</h1>
        <p>{report.cover?.archetype?.tagline}</p>
      </div>
      <div className="accordions">
        {Object.entries(s).map(([key, sec]) => {
          if (!sec || !sec.title) return null;
          return (
            <Accordion key={key} title={sec.title} isOpen={expanded[key]} onToggle={() => toggle(key)} isLocked={sec.locked_fields?.length > 0}>
              {renderContent(key, sec)}
            </Accordion>
          );
        })}
      </div>
    </div>
  );
}

// --- 탭 3: 일운 (7일) ---
function DailyTab({ token, profile }) {
  const [data, setData] = useState(null);
  const [err, setErr] = useState(null);

  useEffect(() => {
    if (!token || !profile) return;
    fetch(`${API_BASE}/saju/daily`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ ...profile, days: 7 })
    })
      .then(res => { if (!res.ok) throw new Error(res.status); return res.json(); })
      .then(d => setData(d.daily))
      .catch(e => setErr(e.message));
  }, [token, profile]);

  if (err === '403') return <div className="center-msg">구독자 전용 기능입니다.</div>;
  if (err) return <div className="center-msg">오류: {err}</div>;
  if (!data) return <div className="center-msg">로딩 중...</div>;

  return (
    <div className="tab-pane scroll">
      <h2>7일간의 일운</h2>
      {data.items.map((item, i) => (
        <div key={i} className="card">
          <div className="card-head">
            <span>{item.date}</span>
            <strong className={`grade-${item.grade}`}>{item.grade_label}</strong>
          </div>
          <h3>{item.name}</h3>
          <p>{item.headline}</p>
          <div className="tip">
            <p>💡 {item.lean_into}</p>
            <p>⚠️ {item.watch_for}</p>
          </div>
        </div>
      ))}
    </div>
  );
}

// --- 탭 4: 케미 (궁합) ---
function CompatTab({ token, profile }) {
  const [partnerBd, setPartnerBd] = useState('1995-05-05');
  const [relType, setRelType] = useState('romance');
  const [result, setResult] = useState(null);
  const [err, setErr] = useState(null);

  const handleCalc = () => {
    setResult(null);
    setErr(null);
    fetch(`${API_BASE}/saju/compatibility`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({
        person_a: profile,
        person_b: { birth_date: partnerBd, birth_time: '12:00:00', birth_location: 'seoul', gender: 'F', lang: 'ko' },
        relationship_type: relType,
        lang: 'ko'
      })
    })
      .then(res => { if (!res.ok) throw new Error(res.status); return res.json(); })
      .then(d => setResult(d.compatibility))
      .catch(e => setErr(e.message));
  };

  return (
    <div className="tab-pane scroll">
      <h2>케미 보기</h2>
      <div className="card">
        <label>상대방 생년월일 <input type="date" value={partnerBd} onChange={e => setPartnerBd(e.target.value)} /></label>
        <label>관계 유형
          <select value={relType} onChange={e => setRelType(e.target.value)}>
            <option value="romance">💖 연애</option>
            <option value="business">💼 비즈니스</option>
            <option value="friend">🤝 친구</option>
            <option value="family">🏠 가족</option>
          </select>
        </label>
        <button className="primary-btn" onClick={handleCalc}>케미 분석하기</button>
      </div>

      {err === '403' && <div className="center-msg">구독자 전용 기능입니다.</div>}
      {err && err !== '403' && <div className="center-msg">오류: {err}</div>}

      {result && (
        <div className="card">
          <h3>{result.overall.grade_label}</h3>
          <p>{result.overall.headline}</p>
          <p>{result.overall.body}</p>
          <div className="axes">
            {Object.entries(result.axes).map(([k, v]) => (
              <div key={k} className="axis-item">
                <strong>{k.toUpperCase()}</strong>
                <p>{v.headline}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// --- 탭 5: 설정 ---
function SettingsTab({ profile, reset }) {
  return (
    <div className="tab-pane scroll">
      <h2>설정</h2>
      <div className="card">
        <p>생년월일: {profile.birth_date}</p>
        <p>출생지: {profile.birth_location}</p>
        <button className="secondary-btn" onClick={reset}>정보 다시 입력하기</button>
      </div>
    </div>
  );
}

// --- 메인 앱 ---
export default function App() {
  const [token, setToken] = useState(null);
  const [profile, setProfile] = useState(null);
  const [report, setReport] = useState(null);
  const [activeTab, setActiveTab] = useState('home');
  const [expanded, setExpanded] = useState({ core: true });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (window.Telegram?.WebApp) { window.Telegram.WebApp.ready(); window.Telegram.WebApp.expand(); }
    const init = async () => {
      let tk = localStorage.getItem('saju_token');
      if (!tk) {
        try {
          const res = await fetch(`${API_BASE}/auth/anonymous`, { method: 'POST' });
          const d = await res.json();
          tk = d.access_token;
          localStorage.setItem('saju_token', tk);
        } catch (e) { console.error(e); }
      }
      setToken(tk);
      const p = localStorage.getItem('saju_profile');
      if (p) setProfile(JSON.parse(p));
      setLoading(false);
    };
    init();
  }, []);

  useEffect(() => {
    if (!profile || !token) return;
    setLoading(true);
    fetch(`${API_BASE}/saju/report`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify(profile)
    })
      .then(r => r.json())
      .then(d => setReport(d.report))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [profile, token]);

  if (loading) return <div className="center-msg">우주의 기운을 계산 중입니다...</div>;
  if (!profile) return <Onboarding onSubmit={(p) => { localStorage.setItem('saju_profile', JSON.stringify(p)); setProfile(p); }} />;
  if (!report) return <div className="center-msg">데이터를 불러오지 못했습니다.</div>;

  return (
    <div className="app-container">
      <div className="main-content">
        {activeTab === 'home' && <HomeTab report={report} expanded={expanded} toggle={(k) => setExpanded(p => ({ ...p, [k]: !p[k] }))} />}
        {activeTab === 'daily' && <DailyTab token={token} profile={profile} />}
        {activeTab === 'compat' && <CompatTab token={token} profile={profile} />}
        {activeTab === 'settings' && <SettingsTab profile={profile} reset={() => { localStorage.removeItem('saju_profile'); setProfile(null); }} />}
      </div>

      <div className="bottom-nav">
        <button className={activeTab === 'home' ? 'active' : ''} onClick={() => setActiveTab('home')}><span>📜</span>리포트</button>
        <button className={activeTab === 'daily' ? 'active' : ''} onClick={() => setActiveTab('daily')}><span>☀️</span>일운</button>
        <button className={activeTab === 'compat' ? 'active' : ''} onClick={() => setActiveTab('compat')}><span>🤝</span>케미</button>
        <button className={activeTab === 'settings' ? 'active' : ''} onClick={() => setActiveTab('settings')}><span>⚙️</span>설정</button>
      </div>
    </div>
  );
}