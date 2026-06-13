// Development helper: unregister any existing service workers to avoid stale cached assets
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations().then(regs => {
    regs.forEach(r => r.unregister().catch(()=>{}));
    console.log('Dev: unregistered existing service workers');
  }).catch(()=>{});
}

const log = document.getElementById('log');
const btnUpdate = document.getElementById('btnUpdate');
const btnPredict = document.getElementById('btnPredict');
const progressContainer = document.getElementById('progressContainer');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');

let progressInterval = null;

function setProgress(percent) {
  progressBar.style.width = percent + '%';
  progressText.textContent = percent + '%';
}

function showProgress() {
  progressContainer.style.display = 'block';
  setProgress(0);
}

function hideProgress() {
  progressContainer.style.display = 'none';
  setProgress(0);
  progressText.textContent = '';
  if (progressInterval) {
    clearInterval(progressInterval);
    progressInterval = null;
  }
}

function simulateProgress() {
  let progress = 0;
  
  progressInterval = setInterval(() => {
    if (progress < 30) {
      progress += Math.random() * 10;
    } else if (progress < 85) {
      progress += Math.random() * 3;
    } else if (progress < 95) {
      progress += Math.random() * 1;
    } else {
      progress = 95;
    }
    
    setProgress(Math.min(Math.floor(progress), 95));
  }, 100);
}

function completeProgress() {
  if (progressInterval) {
    clearInterval(progressInterval);
  }
  setProgress(100);
  
  setTimeout(() => {
    hideProgress();
  }, 500);
}

function setLog(txt, isLoading = false, isError = false, options = {}) {
  const statusBox = log.parentElement;
  statusBox.classList.remove('loading', 'success', 'error');
  
  if (isLoading) {
    statusBox.classList.add('loading');
    log.innerHTML = `<div class="loading-content"><span class="spinner"></span><span>${txt}</span></div>`;
    if (options.progress) {
      // Only the dataset refresh should show progress.
      showProgress();
      if (!progressInterval) simulateProgress();
    } else {
      hideProgress();
    }
  } else if (isError) {
    statusBox.classList.add('error');
    log.textContent = txt;
    hideProgress();
  } else {
    statusBox.classList.add('success');
    log.textContent = txt;
    hideProgress();
  }
}

// Reloj en tiempo real
function startClock() {
  const clockEl = document.getElementById('clock');
  if (!clockEl) return;
  function update() {
    const now = new Date();
    const dateStr = now.toLocaleDateString();
    const timeStr = now.toLocaleTimeString();
    clockEl.textContent = `${dateStr} ${timeStr}`;
  }
  update();
  setInterval(update, 1000);
}

// Iniciar reloj
startClock();

function displayResults(numeros, boliyapa) {
  hideProgress();
  let html = '<div class="results-grid">';
  
  for (const num of numeros) {
    html += `<div class="number-card">${num}</div>`;
  }
  
  html += `<div class="boliyapa-card">
    Boliyapa (7ª Bola)<br>
    <div class="boliyapa-number">${boliyapa}</div>
  </div></div>`;
  
  log.parentElement.classList.remove('loading', 'error');
  log.parentElement.classList.add('success');
  log.innerHTML = html;
}

btnUpdate.addEventListener('click', async ()=>{
  btnUpdate.disabled = true;
  btnPredict.disabled = true;
  setLog('Descargando datos...', true, false, { progress: true });
  
  try{
    const res = await fetch('/update',{method:'POST'});
    const j = await res.json();
    
    completeProgress();
    
    if(j.status==='ok') {
      setLog(`✅ Dataset actualizado\n${j.rows} registros • Última fecha: ${j.ultima_fecha}`);
    } else {
      setLog(`⚠️ ${j.message || 'Error desconocido'}`, false, true);
    }
  }catch(e){
    completeProgress();
    setLog(`❌ Error de conexión: ${e.message}`, false, true);
  }finally{
    btnUpdate.disabled = false;
    btnPredict.disabled = false;
  }
})

btnPredict.addEventListener('click', async ()=>{
  btnUpdate.disabled = true;
  btnPredict.disabled = true;
  setLog('Analizando patrones...', false);
  
  try{
    const res = await fetch('/predict');
    const j = await res.json();
    
    if(j.status==='ok') {
      displayResults(j.numeros_recomendados, j.boliyapa);
    } else {
      setLog(`⚠️ ${j.message || 'Error al predecir'}`, false, true);
    }
  }catch(e){
    completeProgress();
    setLog(`❌ Error de conexión: ${e.message}`, false, true);
  }finally{
    btnUpdate.disabled = false;
    btnPredict.disabled = false;
  }
})
