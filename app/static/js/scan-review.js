(()=>{
  const root=document.getElementById('reviewApp');
  const id=root.dataset.itemId;
  const household=['no_kk','nama_kepala_keluarga','alamat','rt','rw','kode_pos','dusun','desa','kecamatan','kabupaten','provinsi'];
  const memberFields=['status_hubungan','nik','nama_lengkap','jenis_kelamin','tempat_lahir','tanggal_lahir','agama','pendidikan','jenis_pekerjaan','status_perkawinan','kewarganegaraan','no_paspor','no_kitas_kitap','nama_ayah','nama_ibu','golongan_darah'];
  let original={kk:{},members:{}};
  const escapeHtml=value=>String(value??'').replace(/[&<>'"]/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
  async function api(url,options={}){options.headers={...(options.headers||{}),'X-CSRF-Token':CSRF_TOKEN};if(options.json){options.headers['Content-Type']='application/json';options.body=JSON.stringify(options.json);delete options.json}const response=await fetch(url,options),data=await response.json();if(!response.ok)throw new Error(typeof data.detail==='string'?data.detail:(data.detail?.message||'Gagal'));return data}
  const field=(scope,key,value)=>{const automatic=scope==='kk'&&key==='dusun';return `<label>${escapeHtml(automatic?'dusun (otomatis dari alamat)':key.replaceAll('_',' '))}<input data-scope="${scope}" data-field="${key}" type="${key==='tanggal_lahir'?'date':'text'}" value="${escapeHtml(value)}"${automatic?' readonly':''}></label>`};
  const values=(fields,source)=>Object.fromEntries(fields.map(key=>[key,source?.[key]??null]));
  const unchanged=(current,previous)=>Object.keys(current).every(key=>current[key]===previous[key]);
  function payload(scope){const body={};document.querySelectorAll(`[data-scope="${scope}"]`).forEach(input=>body[input.dataset.field]=input.value||null);return body}
  const currentMembers=()=>Object.fromEntries([...document.querySelectorAll('[data-member-id]')].map(member=>[member.dataset.memberId,payload(member.dataset.memberId)]));
  async function saveAll(){
    const button=document.getElementById('saveAll');button.disabled=true;button.textContent='Menyimpan...';
    try{
      const kk=payload('kk');const members=currentMembers();const changes=[];
      if(!unchanged(kk,original.kk))changes.push(api(`/api/scan-items/${id}/kk`,{method:'PATCH',json:kk}));
      for(const [memberId,member] of Object.entries(members))if(!unchanged(member,original.members[memberId]||{}))changes.push(api(`/api/members/${memberId}`,{method:'PATCH',json:member}));
      await Promise.all(changes);
      original={kk,members};
      return true;
    }finally{button.disabled=false;button.textContent='Simpan perubahan'}
  }
  async function load(){
    const data=await api(`/api/scan-items/${id}`);
    if(data.status==='FAILED'){root.innerHTML=`<div class="error">${escapeHtml(data.failure_message||data.failure_code)}</div>`;return}
    original={kk:values(household,data.kk),members:Object.fromEntries(data.members.map(member=>[member.id,values(memberFields,member)]))};
    const issues=data.issues.filter(issue=>!issue.resolved);
    const issueList=issues.length?`<section class="issue-summary"><h2>Perlu diperiksa</h2>${issues.map(issue=>`<p>${escapeHtml(issue.message)}</p>`).join('')}</section>`:'<section class="issue-summary success"><h2>Hasil valid</h2></section>';
    root.innerHTML=`<div class="review-layout"><div class="review-content">${issueList}<details class="document-preview"><summary>Preview dokumen KK <span class="badge">${escapeHtml(data.status)}</span></summary><img src="/api/scan-items/${id}/thumbnail" alt="Preview dokumen KK"></details><section class="form-section"><h2>Data KK</h2><div class="form-grid">${household.map(key=>field('kk',key,data.kk?.[key])).join('')}</div></section><section class="form-section"><h2>Anggota keluarga</h2>${data.members.map((member,index)=>`<details class="member" data-member-id="${member.id}" ${issues.length||index===0?'open':''}><summary>#${member.no_urut_kk} ${escapeHtml(member.nama_lengkap||'Nama belum terbaca')}</summary><div class="member-fields">${memberFields.map(key=>field(member.id,key,member[key])).join('')}</div></details>`).join('')}</section><div class="review-actions"><button id="saveAll" type="button">Simpan perubahan</button><button class="primary" id="approve" type="button">Setujui data</button></div></div></div>`;
    document.getElementById('saveAll').onclick=async()=>{try{await saveAll();await load()}catch(error){alert(error.message)}};
    document.getElementById('approve').onclick=async()=>{try{const ok=await saveAll();if(!ok)return;const approved=await api(`/api/scan-items/${id}/approve`,{method:'POST'});location.href=`/batches/${approved.batch_id}`}catch(error){alert(error.message)}};
  }
  load().catch(error=>root.innerHTML=`<div class="error">${escapeHtml(error.message)}</div>`);
})();
