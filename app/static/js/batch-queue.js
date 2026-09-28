(()=>{
  const galleryInput=document.getElementById('galleryInput');
  const dropZone=document.getElementById('pdfDropZone');
  const uploadHint=document.getElementById('uploadHint');
  const selection=document.getElementById('selection');
  const queueList=document.getElementById('queueList');
  const queueHint=document.getElementById('queueHint');
  const clearQueue=document.getElementById('clearQueue');
  const galleryButton=document.getElementById('galleryBtn');
  const resume=document.getElementById('resume');
  const resumeButton=document.getElementById('resumeBtn');
  const startButton=document.getElementById('startBtn');
  const progress=document.getElementById('processProgress');
  let pending=[];
  let running=false;

  const toast=message=>{const element=document.getElementById('toast');element.textContent=message;element.classList.add('show');setTimeout(()=>element.classList.remove('show'),2600)};
  const escapeHtml=value=>String(value).replace(/[&<>'"]/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
  async function api(url,options={}){options.headers={...(options.headers||{}),'X-CSRF-Token':CSRF_TOKEN};const response=await fetch(url,options);const data=await response.json();if(!response.ok)throw new Error(typeof data.detail==='string'?data.detail:'Request gagal');return data}
  function render(){
    selection.classList.toggle('hidden',!pending.length);
    startButton.textContent=`Proses ${pending.length} PDF`;
    startButton.disabled=running||!pending.length;
    queueHint.textContent=pending.length?`${pending.length} PDF siap diproses satu per satu.`:'Antrean kosong.';
    uploadHint.textContent=pending.length?`${pending.length} PDF siap. Tambahkan lagi atau mulai proses.`:'Atau pilih PDF dari perangkat. Maksimal 20 dokumen, masing-masing 8 MB.';
    queueList.innerHTML=pending.map((item,index)=>`<div class="queue-item"><b>${index+1}</b><div><strong>${escapeHtml(item.filename)}</strong><small>${(item.blob.size/1048576).toFixed(2)} MB · PDF teks</small></div><button class="queue-remove" data-index="${index}" type="button" aria-label="Hapus ${escapeHtml(item.filename)}">Hapus</button></div>`).join('');
    queueList.querySelectorAll('.queue-remove').forEach(button=>button.onclick=()=>{if(running)return;pending.splice(Number(button.dataset.index),1);render()});
  }
  async function add(files){
    const incoming=[...files];
    if(pending.length+incoming.length>20){toast('Maksimal 20 dokumen dalam satu batch');return}
    let added=0;
    for(const file of incoming){
      try{
        const item=await ImagePreprocessor.prepare(file);
        if(item.sourceType!=='pdf')throw new Error('Gunakan PDF KK dengan teks selectable');
        pending.push(item);added++;
      }catch(error){toast(error.message)}
    }
    if(added)render();
  }
  function setDragging(active){dropZone.classList.toggle('is-dragging',active);if(active)uploadHint.textContent='Lepaskan PDF untuk menambahkannya ke antrean.'}
  galleryInput.onchange=event=>{add(event.target.files);galleryInput.value=''};
  galleryButton.onclick=event=>{event.stopPropagation();galleryInput.click()};
  dropZone.onclick=()=>galleryInput.click();
  dropZone.onkeydown=event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();galleryInput.click()}};
  for(const eventName of ['dragenter','dragover'])dropZone.addEventListener(eventName,event=>{event.preventDefault();event.stopPropagation();setDragging(true)});
  for(const eventName of ['dragleave','dragend'])dropZone.addEventListener(eventName,event=>{event.preventDefault();if(!dropZone.contains(event.relatedTarget))setDragging(false)});
  dropZone.addEventListener('drop',event=>{event.preventDefault();event.stopPropagation();setDragging(false);add(event.dataTransfer.files)});
  clearQueue.onclick=()=>{if(running)return;pending=[];render()};

  async function process(items){
    progress.classList.remove('hidden');
    for(let index=0;index<items.length;index++){
      const item=items[index];
      progress.textContent=`Memproses ${index+1} dari ${items.length}: ${item.filename}`;
      const formData=new FormData();formData.append('file',item.blob,item.filename);
      try{
        const result=await api(`/api/scan-items/${item.id}/process`,{method:'POST',body:formData});
        if(result.status!=='FAILED'||['DUPLICATE_DOCUMENT','DUPLICATE_HOUSEHOLD'].includes(result.failure_code))await QueueDB.remove(item.id);
      }catch(error){toast(`${item.filename}: ${error.message}`)}
    }
  }
  startButton.onclick=async()=>{
    if(running||!pending.length)return;
    running=true;render();
    try{
      const batch=await api('/api/batches',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({filenames:pending.map(item=>item.filename)})});
      const records=[];
      for(let index=0;index<batch.items.length;index++){
        const record={id:batch.items[index].id,batchId:batch.id,filename:pending[index].filename,blob:pending[index].blob,sourceType:'pdf'};
        records.push(record);await QueueDB.put(record);
      }
      await process(records);
      location.href=`/batches/${batch.id}`;
    }finally{running=false;progress.classList.add('hidden');render()}
  };
  QueueDB.all().then(items=>{if(items.length){resume.classList.remove('hidden');resumeButton.onclick=()=>process(items)}});
  render();
})();
