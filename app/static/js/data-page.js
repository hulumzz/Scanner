(()=>{
  const query=document.getElementById('dataSearch');
  const status=document.getElementById('statusFilter');
  const output=document.getElementById('dataTable');
  const meta=document.getElementById('dataMeta');
  const prev=document.getElementById('prevPage');
  const next=document.getElementById('nextPage');
  const limit=30;
  let offset=0;
  let debounce;
  const escapeHtml=value=>String(value??'').replace(/[&<>'"]/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
  async function load(){
    const params=new URLSearchParams({offset:String(offset),limit:String(limit)});
    if(query.value.trim())params.set('q',query.value.trim());
    if(status.value)params.set('status',status.value);
    const response=await fetch('/api/data?'+params);
    const data=await response.json();
    if(!response.ok)throw new Error(data.detail||'Gagal memuat data');
    meta.textContent=data.total?`Menampilkan ${offset+1}–${Math.min(offset+data.items.length,data.total)} dari ${data.total} data.`:'Belum ada data.';
    output.innerHTML=`<table><tr><th>No. KK</th><th>Kepala Keluarga</th><th>Anggota</th><th>Status</th><th></th></tr>${data.items.map(item=>`<tr><td>${escapeHtml(item.no_kk||'-')}</td><td>${escapeHtml(item.nama_kepala_keluarga||'-')}</td><td>${item.member_count}</td><td><span class="badge">${escapeHtml(item.status)}</span></td><td><a href="/scans/${item.id}">Buka</a></td></tr>`).join('')}</table>`;
    prev.disabled=offset===0;next.disabled=offset+limit>=data.total;
  }
  const refresh=()=>load().catch(error=>output.innerHTML=`<p class="error">${escapeHtml(error.message)}</p>`);
  query.oninput=()=>{clearTimeout(debounce);debounce=setTimeout(()=>{offset=0;refresh()},300)};
  status.onchange=()=>{offset=0;refresh()};
  prev.onclick=()=>{offset=Math.max(0,offset-limit);refresh()};
  next.onclick=()=>{offset+=limit;refresh()};
  refresh();
})();
