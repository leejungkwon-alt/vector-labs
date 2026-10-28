import { useState, useEffect } from 'react';
import './App.css';

const API_BASE = 'https://vector-labs-api-787049663118.asia-northeast3.run.app/api/v1';

const getTgLang = () => {
  const tgLang = window.Telegram?.WebApp?.initDataUnsafe?.user?.language_code || 'en';
  if (tgLang.startsWith('ko')) return 'ko';
  if (tgLang.startsWith('ja')) return 'ja';
  if (tgLang.startsWith('zh')) return 'zh_cn';
  if (tgLang.startsWith('es')) return 'es';
  return 'en';
};

const TEXTS = {
  ko: {
    loading: "우주의 기운을 계산 중입니다...",
    error: "오류",
    subscriberOnly: "구독자 전용 기능입니다.",
    compatCalc: "케미 분석하기",
    partnerBd: "상대방 생년월일",
    relType: "관계 유형",
    romance: "연애", business: "비즈니스", friend: "친구", family: "가족",
    onboardingTitle: "당신의 결을 읽어냅니다.",
    onboardingSub: "출생 정보를 입력해 주세요.",
    birthDate: "생년월일", birthTime: "출생 시간", gender: "성별", location: "출생지",
    male: "남성", female: "여성",
    submit: "결 확인하기",
    reset: "정보 다시 입력하기",
    locked: "더 깊은 분석은 프리미엄에서 확인하세요.",
    tabs: { home: "리포트", daily: "일운", compat: "케미", settings: "설정" }
  },
  en: {
    loading: "Calculating the energy of the universe...",
    error: "Error",
    subscriberOnly: "Subscriber-only feature.",
    compatCalc: "Analyze Chemistry",
    partnerBd: "Partner's birthday",
    relType: "Relationship type",
    romance: "Romance", business: "Business", friend: "Friend", family: "Family",
    onboardingTitle: "Reading the grain of your life.",
    onboardingSub: "Please enter your birth information.",
    birthDate: "Birth Date", birthTime: "Birth Time", gender: "Gender", location: "Birthplace",
    male: "Male", female: "Female",
    submit: "See Result",
    reset: "Re-enter Information",
    locked: "Deeper analysis is available in Premium.",
    tabs: { home: "Report", daily: "Daily", compat: "Chemistry", settings: "Settings" }
  }
};

const getText = (lang) => TEXTS[lang] || TEXTS.en;

// --- 공통 컴포넌트 ---
function Accordion({ title, isOpen, onToggle, children, isLocked, text }) {
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
              <span>🔒</span> {text.locked}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// --- 탭 1: 온보딩 ---
function Onboarding({ onSubmit, text }) {
  const [bd, setBd] = useState('1995-05-05');
  const [bt, setBt] = useState('12:00');
  const [gender, setGender] = useState('M');
  const [loc, setLoc] = useState('seoul');

  return (
    <div className="onboarding">
      <div className="onboarding-card">
        <h1>Gyeol</h1>
        <p>{text.onboardingTitle}<br/>{text.onboardingSub}</p>
        <form onSubmit={(e) => { 
          e.preventDefault(); 
          onSubmit({ birth_date: bd, birth_time: bt + ':00', birth_location: loc, gender, lang: getTgLang() }); 
        }}>
          <label>{text.birthDate} <input type="date" value={bd} onChange={e => setBd(e.target.value)} required /></label>
          <label>{text.birthTime} <input type="time" value={bt} onChange={e => setBt(e.target.value)} required /></label>
          <label>{text.gender}
            <select value={gender} onChange={e => setGender(e.target.value)}>
              <option value="M">{text.male}</option><option value="F">{text.female}</option>
            </select>
          </label>
          <label>{text.location}
            <select value={loc} onChange={e => setLoc(e.target.value)}>
              <option value="seoul">서울 (Seoul)</option><option value="busan">부산 (Busan)</option>              
              <option value="new_york">뉴욕 (New York)</option><option value="tokyo">도쿄 (Tokyo)</option>
            </select>
          </label>
          <button type="submit" className="primary-btn">{text.submit}</button>
        </form>
      </div>
    </div>
  );
}

// --- 탭 2: 홈 (리포트 뷰어) ---
function HomeTab({ report, expanded, toggle, text }) {
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
        return <div><p>• Core Element: {sec.power?.element}</p><p>• Colors: {sec.power?.colors?.join(', ')}</p></div>;
      case 'health':
        return sec.blocks?.map((b, i) => <div key={i} className="item"><strong>{b.name}</strong><p>{b.body}</p></div>);
      case 'money':
      case 'work':
      case 'bonds':
        return <div><h4>{sec.headline}</h4><p>{sec.body}</p></div>;
      case 'timeline':
        return sec.items?.map((i, idx) => <div key={idx} className="item-row"><span>{i.ages[0]}~{i.ages[1]} yrs ({i.pillar})</span><strong>{i.grade}</strong></div>);
      case 'monthly':
        return sec.items?.map((i, idx) => <div key={idx} className="item"><strong>{i.approx_solar_month} ({i.pillar})</strong><p>{i.headline}</p></div>);
      default:
        return <p className="text-muted">Content coming soon.</p>;
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
            <Accordion key={key} title={sec.title} isOpen={expanded[key]} onToggle={() => toggle(key)} isLocked={sec.locked_fields?.length > 0} text={text}>
              {renderContent(key, sec)}
            </Accordion>
          );
        })}
      </div>
    </div>
  );
}

// --- 탭 3: 일운 (7일) ---
function DailyTab({ token, profile, text }) {
  const [data, setData] = useState(null);
  const [err, setErr] = useState(null);

  useEffect(() => {
    if (!token || !profile) return;
    fetch(`${API_BASE}/saju/daily`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ ...profile, days: 7 })
    })
      .then(async res => {
        if (!res.ok) {
          const errBody = await res.json().catch(() => ({}));
          const errorMsg = errBody.detail ? (typeof errBody.detail === 'string' ? errBody.detail : JSON.stringify(errBody.detail)) : res.status;
          throw new Error(`${res.status}: ${errorMsg}`);
        }
        return res.json();
      })
      .then(d => setData(d.daily))
      .catch(e => setErr(e.message));
  }, [token, profile]);

  if (err?.startsWith('403')) return <div className="center-msg">{text.subscriberOnly}</div>;
  if (err) return <div className="center-msg">{text.error}: {err}</div>;
  if (!data) return <div className="center-msg">{text.loading}</div>;

  return (
    <div className="tab-pane scroll">
      <h2>{text.tabs.daily}</h2>
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
function CompatTab({ token, profile, text }) {
  const [partnerBd, setPartnerBd] = useState('1995-05-05');
  const [relType, setRelType] = useState('romance');
  const [result, setResult] = useState(null);
  const [err, setErr] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCalc = () => {
    setResult(null);
    setErr(null);
    setLoading(true);

    const personA = { ...profile, lang: profile.lang || 'en' };
    delete personA.lang;
    
    const personB = { 
      birth_date: partnerBd, 
      birth_time: '12:00:00', 
      birth_time_mode: 'exact', // 👈 422 에러 해결을 위해 명시적 추가
      birth_location: 'seoul', 
      gender: 'F', 
      
    };

    fetch(`${API_BASE}/saju/compatibility`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({
        person_a: personA,
        person_b: personB,
        relationship_type: relType,
        lang: profile.lang || 'en'
      })
    })
      .then(async res => {
        if (!res.ok) {
          const errBody = await res.json().catch(() => ({}));
          const errorMsg = errBody.detail ? (typeof errBody.detail === 'string' ? errBody.detail : JSON.stringify(errBody.detail)) : res.status;
          throw new Error(`${res.status}: ${errorMsg}`);
        }
        return res.json();
      })
      .then(d => setResult(d.compatibility))
      .catch(e => setErr(e.message))
      .finally(() => setLoading(false));
  };

  return (
    <div className="tab-pane scroll">
      <h2>{text.tabs.compat}</h2>
      <div className="card">
        <label>{text.partnerBd} <input type="date" value={partnerBd} onChange={e => setPartnerBd(e.target.value)} /></label>
        <label>{text.relType}
          <select value={relType} onChange={e => setRelType(e.target.value)}>
            <option value="romance">💖 {text.romance}</option>
            <option value="business">💼 {text.business}</option>
            <option value="friend">🤝 {text.friend}</option>
            <option value="family">🏠 {text.family}</option>
          </select>
        </label>
        <button className="primary-btn" onClick={handleCalc} disabled={loading}>
          {loading ? '...' : text.compatCalc}
        </button>
      </div>

      {err?.startsWith('403') && <div className="center-msg">{text.subscriberOnly}</div>}
      {err && !err.startsWith('403') && <div className="center-msg" style={{wordBreak: 'break-all'}}>{text.error}: {err}</div>}

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
function SettingsTab({ profile, reset, text }) {
  return (
    <div className="tab-pane scroll">
      <h2>{text.tabs.settings}</h2>
      <div className="card">
        <p>{text.birthDate}: {profile.birth_date}</p>
        <p>{text.location}: {profile.birth_location}</p>
        <button className="secondary-btn" onClick={reset}>{text.reset}</button>
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

  const text = getText(getTgLang());

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
      body: JSON.stringify({ ...profile, lang: profile.lang || 'en' })
    })
      .then(async res => {
        if (!res.ok) {
          const errBody = await res.json().catch(() => ({}));
          const errorMsg = errBody.detail ? (typeof errBody.detail === 'string' ? errBody.detail : JSON.stringify(errBody.detail)) : res.status;
          throw new Error(`${res.status}: ${errorMsg}`);
        }
        return res.json();
      })
      .then(d => setReport(d.report))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [profile, token]);

  if (loading) return <div className="center-msg">{text.loading}</div>;
  if (!profile) return <Onboarding onSubmit={(p) => { localStorage.setItem('saju_profile', JSON.stringify(p)); setProfile(p); }} text={text} />;
  if (!report) return <div className="center-msg">{text.error}: Failed to load report.</div>;

  return (
    <div className="app-container">
      <div className="main-content">
        {activeTab === 'home' && <HomeTab report={report} expanded={expanded} toggle={(k) => setExpanded(p => ({ ...p, [k]: !p[k] }))} text={text} />}
        {activeTab === 'daily' && <DailyTab token={token} profile={profile} text={text} />}
        {activeTab === 'compat' && <CompatTab token={token} profile={profile} text={text} />}
        {activeTab === 'settings' && <SettingsTab profile={profile} reset={() => { localStorage.removeItem('saju_profile'); setProfile(null); }} text={text} />}
      </div>

      <div className="bottom-nav">
        <button className={activeTab === 'home' ? 'active' : ''} onClick={() => setActiveTab('home')}><span>📜</span>{text.tabs.home}</button>
        <button className={activeTab === 'daily' ? 'active' : ''} onClick={() => setActiveTab('daily')}><span>☀️</span>{text.tabs.daily}</button>
        <button className={activeTab === 'compat' ? 'active' : ''} onClick={() => setActiveTab('compat')}><span>🤝</span>{text.tabs.compat}</button>
        <button className={activeTab === 'settings' ? 'active' : ''} onClick={() => setActiveTab('settings')}><span>⚙️</span>{text.tabs.settings}</button>
      </div>
    </div>
  );
}