(()=>{
  const root=document.getElementById('batchList');
  const batchId=root.dataset.batchId;
  const summary=document.getElementById('batchSummary');
  const subtitle=document.getElementById('batchSubtitle');
  const actionHint=document.getElementById('batchActionHint');
  const approveButton=document.getElementById('approveExtracted');
  const reviewNext=document.getElementById('reviewNext');
  const filters=document.getElementById('batchFilters');
  let batch=null;
  let filter='';
  const labels={QUEUED:'Menunggu',PROCESSING:'Diproses',EXTRACTED:'Siap disetujui',REVIEW_REQUIRED:'Perlu review',APPROVED:'Disetujui',FAILED:'Gagal'};
  const toast=message=>{const element=document.getElementById('toast');element.textContent=message;element.classList.add('show');setTimeout(()=>element.classList.remove('show'),2600)};
  const escapeHtml=value=>String(value||'').replace(/[&<>'"]/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
  async function api(url,options={}){options.headers={...(options.headers||{}),'X-CSRF-Token':CSRF_TOKEN};const response=await fetch(url,options);const data=await response.json();if(!response.ok)throw new Error(typeof data.detail==='string'?data.detail:'Request gagal');return data}
  const card=(label,value)=>`<div><span>${label}</span><b>${value}</b></div>`;
  function render(){
    subtitle.textContent=`${batch.total} dokumen`;
    summary.innerHTML=[card('Siap disetujui',batch.extracted),card('Perlu review',batch.review_required),card('Disetujui',batch.approved),card('Gagal',batch.failed)].join('');
    approveButton.disabled=!batch.extracted;
    approveButton.textContent=batch.extracted?`Setujui semua (${batch.extracted})`:'Tidak ada data valid';
    const next=batch.items.find(item=>item.status==='REVIEW_REQUIRED')||batch.items.find(item=>item.status==='EXTRACTED');
    reviewNext.href=next?`/scans/${next.id}`:'#';
    reviewNext.classList.toggle('disabled',!next);
    actionHint.textContent=batch.review_required?`${batch.review_required} perlu diperiksa.`:batch.extracted?`${batch.extracted} siap disetujui.`:'Selesai.';
    const items=filter?batch.items.filter(item=>item.status===filter):batch.items;
    root.innerHTML=items.map(item=>`<article class="batch-item"><div><small>KK-${String(item.item_number).padStart(3,'0')}</small><h3>${escapeHtml(item.original_filename)}</h3><p>${item.failure_message?escapeHtml(item.failure_message):labels[item.status]}</p></div><div class="batch-item-actions"><span class="badge badge-${item.status.toLowerCase()}">${labels[item.status]}</span><a class="btn" href="/scans/${item.id}">${item.status==='FAILED'?'Lihat alasan':'Buka'}</a></div></article>`).join('')||'<p class="empty-state">Tidak ada dokumen pada filter ini.</p>';
  }
  async function load(){batch=await api(`/api/batches/${batchId}`);render()}
  filters.querySelectorAll('button').forEach(button=>button.onclick=()=>{filter=button.dataset.filter;filters.querySelectorAll('button').forEach(item=>item.classList.toggle('active',item===button));render()});
  approveButton.onclick=async()=>{if(!batch.extracted)return;approveButton.disabled=true;try{const result=await api(`/api/batches/${batchId}/approve-extracted`,{method:'POST'});batch=result.batch;toast(`${result.approved_count} data disetujui`);render()}catch(error){toast(error.message)}};
  load().catch(error=>{root.innerHTML=`<p class="error">${escapeHtml(error.message)}</p>`});
})();
