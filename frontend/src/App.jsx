import React, { useState } from 'react';
const BACKEND = import.meta.env.VITE_API_URL || '';
export default function App(){
  const [q,setQ]=useState('');
  const [resp,setResp]=useState(null);
  const [loading,setLoading]=useState(false);
  async function ask(){
    setLoading(true);
    setResp(null);
    const res = await fetch(BACKEND + '/qa', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({query:q, top_k:4})
    });
    const j = await res.json();
    setResp(j);
    setLoading(false);
  }
  return (
    <div style={{maxWidth:900, margin:'40px auto', fontFamily:'sans-serif'}}>
      <h2>Perplexity-style MVP (Render)</h2>
      <textarea value={q} onChange={(e)=>setQ(e.target.value)} rows={4} style={{width:'100%'}}/>
      <div style={{marginTop:10}}>
        <button onClick={ask} disabled={!q||loading}>Ask</button>
      </div>
      {loading && <p>Thinking...</p>}
      {resp && (
        <div style={{marginTop:20}}>
          <h3>Answer</h3>
          <pre style={{whiteSpace:'pre-wrap'}}>{resp.answer}</pre>
          <h4>Sources</h4>
          <ul>{resp.sources?.map((s,i)=>
            <li key={i}><a href={s.url} target='_blank' rel='noreferrer'>{s.title||s.url}</a></li>
          )}</ul>
        </div>
      )}
    </div>
  );
}
