(()=>{
  const summary=document.getElementById('exportSummary');
  const download=document.getElementById('downloadMaster');
  async function load(){
    const response=await fetch('/api/exports/master-summary');
    const data=await response.json();
    if(!response.ok)throw new Error(data.detail||'Gagal menghitung data');
    summary.textContent=data.kk_count?`${data.kk_count} KK dan ${data.row_count} baris penduduk akan masuk ke satu workbook.`:'Belum ada data approved untuk diunduh.';
    download.classList.toggle('disabled',!data.kk_count);
    download.setAttribute('aria-disabled',String(!data.kk_count));
    if(!data.kk_count)download.onclick=event=>event.preventDefault();
  }
  load().catch(error=>summary.textContent=error.message);
})();
