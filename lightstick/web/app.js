(() => {
  const dot = document.getElementById('connDot');
  const connText = document.getElementById('connText');
  const battVal = document.getElementById('battVal');
  const battBtn = document.getElementById('battBtn');
  const idleBtn = document.getElementById('idleBtn');
  const powerOnBtn = document.getElementById('powerOnBtn');
  const powerOffBtn = document.getElementById('powerOffBtn');
  const startPatternBtn = document.getElementById('startPatternBtn');
  
  const tabLinks = [...document.querySelectorAll('.tab-link')];
  const tabContents = [...document.querySelectorAll('.tab-content')];
  
  const memberCards = [...document.querySelectorAll('.member-card')];
  const effectCards = [...document.querySelectorAll('.effect-card')];
  const comboCards = [...document.querySelectorAll('.combo-card')];
  
  const presetDots = [...document.querySelectorAll('.preset-dot')];
  const colorInput = document.getElementById('colorInput');
  const durSlider = document.getElementById('durSlider');
  const durValue = document.getElementById('durValue');
  
  let ws;
  let reconnectTimer;
  let activeEffect = "solid";
  
  function connect() {
    ws = new WebSocket(`ws://${location.host}/ws`);

    ws.onopen = () => {
      dot.classList.add('live');
      connText.textContent = "Connected";
      clearTimeout(reconnectTimer);
    };

    ws.onclose = () => {
      dot.classList.remove('live');
      connText.textContent = "Disconnected";
      reconnectTimer = setTimeout(connect, 1000);
    };

    ws.onerror = () => ws.close();

    ws.onmessage = (evt) => {
      try {
        const msg = JSON.parse(evt.data);
        if (typeof msg.battery === 'number') {
          battVal.textContent = msg.battery;
        }
      } catch (e) { /* ignore */ }
    };
  }

  function send(obj) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(obj));
    }
  }
  
  const throttledSend = throttle(send, 100);

  // Tab switching
  tabLinks.forEach(link => {
    link.addEventListener('click', () => {
      tabLinks.forEach(l => l.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));
      
      link.classList.add('active');
      const tabId = `tab-${link.dataset.tab}`;
      document.getElementById(tabId).classList.add('active');
    });
  });

  // Clear all visual active states on command inputs
  function clearAllActive() {
    memberCards.forEach(c => c.classList.remove('selected'));
    effectCards.forEach(c => c.classList.remove('active'));
    comboCards.forEach(c => c.classList.remove('active'));
    powerOnBtn.classList.remove('active');
    powerOffBtn.classList.remove('active');
    idleBtn.classList.remove('active');
    startPatternBtn.classList.remove('active');
  }

  // Members selection
  memberCards.forEach(card => {
    card.addEventListener('click', () => {
      clearAllActive();
      card.classList.add('selected');
      send({ member: parseInt(card.dataset.i, 10) });
    });
  });

  // Helper: Hex color to RGB object
  function hexToRgb(hex) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return { r, g, b };
  }

  // Send current color coordinates
  function sendColor(hex) {
    const rgb = hexToRgb(hex);
    throttledSend(rgb);
    
    // Update theme color variable dynamically for visual feedback
    document.documentElement.style.setProperty('--accent', hex);
    document.documentElement.style.setProperty('--accent-glow', `${hex}66`);
  }

  // Preset colors click handler
  presetDots.forEach(dotEl => {
    dotEl.addEventListener('click', () => {
      presetDots.forEach(d => d.classList.remove('active'));
      dotEl.classList.add('active');
      colorInput.value = dotEl.dataset.hex;
      sendColor(dotEl.dataset.hex);
    });
  });

  // Color picker drag handler
  colorInput.addEventListener('input', (e) => {
    presetDots.forEach(d => d.classList.remove('active'));
    sendColor(e.target.value);
  });

  // Slider change duration
  durSlider.addEventListener('input', (e) => {
    const val = parseFloat(e.target.value).toFixed(1);
    durValue.textContent = `${val}s`;
    
    // If an effect card is currently active, we want to update the duration immediately
    const activeFxCard = effectCards.find(c => c.classList.contains('active'));
    if (activeFxCard) {
      const fx = activeFxCard.dataset.fx;
      const durationMs = Math.round(parseFloat(val) * 1000);
      const rgb = hexToRgb(colorInput.value);
      throttledSend({
        effect: fx,
        duration: durationMs,
        ...rgb
      });
    }
  });

  // Custom effect cards click
  effectCards.forEach(card => {
    card.addEventListener('click', () => {
      clearAllActive();
      card.classList.add('active');
      activeEffect = card.dataset.fx;
      
      const val = parseFloat(durSlider.value);
      const durationMs = Math.round(val * 1000);
      const rgb = hexToRgb(colorInput.value);
      
      send({
        effect: activeEffect,
        duration: durationMs,
        ...rgb
      });
    });
  });

  // Start / Activate Light Pattern Mode button
  // Switches the stick into pattern mode using whichever effect is currently
  // selected (falls back to "solid" if none has been picked yet), with the
  // current color + duration settings.
  startPatternBtn.addEventListener('click', () => {
    let card = effectCards.find(c => c.classList.contains('active'));
    if (!card) card = effectCards.find(c => c.dataset.fx === 'solid') || effectCards[0];

    clearAllActive();
    card.classList.add('active');
    startPatternBtn.classList.add('active');
    activeEffect = card.dataset.fx;

    const val = parseFloat(durSlider.value);
    const durationMs = Math.round(val * 1000);
    const rgb = hexToRgb(colorInput.value);

    send({
      effect: activeEffect,
      duration: durationMs,
      ...rgb
    });
  });

  // Audio-visual combo cards click
  comboCards.forEach(card => {
    card.addEventListener('click', () => {
      clearAllActive();
      card.classList.add('active');
      
      const fx = card.dataset.fx;
      send({ effect: fx });
    });
  });

  // Power On
  powerOnBtn.addEventListener('click', () => {
    clearAllActive();
    powerOnBtn.classList.add('active');
    send({ cmd: 'on' });
  });

  // Power Off
  powerOffBtn.addEventListener('click', () => {
    clearAllActive();
    powerOffBtn.classList.add('active');
    send({ cmd: 'off' });
  });

  // Battery Button
  battBtn.addEventListener('click', () => {
    // Battery doesn't clear states since it's transient, but it silences buzzer
    send({ cmd: 'battery' });
  });

  // Idle Button
  idleBtn.addEventListener('click', () => {
    clearAllActive();
    idleBtn.classList.add('active');
    send({ cmd: 'idle' });
  });

  // Throttle helper
  function throttle(func, limit) {
    let inThrottle;
    return function() {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    }
  }

  // Initial color theme update
  document.documentElement.style.setProperty('--accent', colorInput.value);
  document.documentElement.style.setProperty('--accent-glow', `${colorInput.value}66`);

  connect();
})();
