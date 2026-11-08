// Voice and face for the interview: setup choices, listening, speaking, the free
// animated face, and lifelike avatar sessions. Options come from GET /media
// (media.json); paid services are reached through the server so keys stay there.
//
// Used by index.html through window.Media:
//   Media.initSetup(onChange)   render the "Conversation" setup section
//   Media.choice()              {mode, voice, voice_id, face} for /session/create
//   Media.ready()               true when the chosen options are set up
//   Media.begin(data, onBegun, onSpoken)  prepare the interview screen; the callbacks
//                               run when the conversation starts and after the opening line
//   Media.speak(entry)          say a witness transcript entry (promise)
//   Media.listen()              record the interviewer, resolve with their words
//   Media.stop()                end any avatar session

(() => {
  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const $ = (id) => document.getElementById(id);
  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;

  let catalog = null, onChange = () => {};
  let session = null;          // the running interview's {mode, voice, voice_id, face}
  let avatar = null;           // lifelike avatar connection
  let recorder = null, recognizer = null;

  async function getJSON(url, body) {
    const res = await fetch(url, body === undefined ? {} : {
      method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)});
    if (res.status === 401) { location.href = "/login"; throw new Error("Please sign in again."); }
    if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || res.statusText);
    return res.json();
  }

  // -------------------------------------------------------------------------
  // Setup section
  // -------------------------------------------------------------------------

  function choice() {
    const mode = document.querySelector('input[name="convMode"]:checked')?.value || "text";
    if (mode === "text") return {mode};
    const out = {mode, voice: $("voiceSvc").value, voice_id: $("voiceId").value || ""};
    if (mode === "face") out.face = $("faceSvc").value;
    return out;
  }

  function problems() {
    const c = choice(), list = [];
    if (c.mode === "text" || !catalog) return list;
    const v = catalog.voice[c.voice];
    if (!v.status.ready) list.push({kind: "voice", id: c.voice, problems: v.status.problems});
    if (c.voice === "browser" && !SpeechRec)
      list.push({kind: "voice", id: c.voice, problems: [{type: "browser_stt"}]});
    if (c.mode === "face") {
      const f = catalog.face[c.face];
      if (!f.status.ready) list.push({kind: "face", id: c.face, problems: f.status.problems});
      if (f.needs_voice_audio && c.voice === "browser")
        list.push({kind: "face", id: c.face, problems: [{type: "needs_server_voice"}]});
    }
    return list;
  }

  const ready = () => problems().length === 0;

  const openEnv = `Open the <b>.env</b> file in the app folder. <b>Windows:</b> right-click it, choose <b>Open with</b>, then <b>Notepad</b>. <b>Mac:</b> press <b>Cmd+Shift+.</b> to show hidden files, then open it with <b>TextEdit</b>. If there's no .env file, copy <b>.env.example</b> and rename the copy to <b>.env</b>.`;

  function steps(kind, id, p) {
    const prov = catalog[kind][id] || {};
    const name = esc(prov.name || id);
    switch (p.type) {
      case "key": return `<h4>${name} needs an API key</h4><ol>
          <li>Create an account and get a key at <a href="${esc(prov.key_url)}" target="_blank" rel="noopener">${esc(prov.key_url)}</a>.</li>
          <li>${openEnv}</li>
          <li>Add this line, with your key after the <b>=</b> sign (no spaces or quotes): <code>${esc(p.key_env)}=${esc(prov.key_example || "your-key")}</code></li>
          <li>Save the file, then click <b>Check again</b>. You don't need to restart the app.</li></ol>`;
      case "setting": return `<h4>${name} needs one more setting</h4><ol>
          <li>${openEnv}</li>
          <li>Add the line <code>${esc(p.name)}=...</code>, replacing <code>...</code> with: ${esc(p.label)}.</li>
          <li>Save the file, then click <b>Check again</b>.</li></ol>`;
      case "browser_stt": return `<h4>This browser can't recognize speech</h4>
          <p>The free built-in option needs <b>Chrome</b> or <b>Edge</b>. Open the app in one of those, or choose OpenAI, ElevenLabs, or Deepgram as the voice service.</p>`;
      case "needs_server_voice": return `<h4>${name} needs a natural voice</h4>
          <p>It lip-syncs to real audio, so choose <b>OpenAI</b>, <b>ElevenLabs</b>, or <b>Deepgram</b> as the voice service instead of the browser's built-in voice.</p>`;
      default: return `<h4>${name} isn't available</h4>`;
    }
  }

  function infoLine(p) {
    return `${esc(p.note || "")} <span class="badge">Cost: ${esc(p.price || "not listed")}</span>`;
  }

  async function loadVoices() {
    const c = choice(), sel = $("voiceId");
    if (c.mode === "text") return;
    const v = catalog.voice[c.voice];
    let list = [];
    if (c.voice === "browser") {
      const all = speechSynthesis.getVoices();
      list = all.filter(x => x.lang.startsWith("en")).map(x => ({id: x.name, name: `${x.name} (${x.lang})`}));
      if (!list.length) list = all.map(x => ({id: x.name, name: x.name}));
    } else if (v.status.ready) {
      try { list = await getJSON(`/media/voices?provider=${encodeURIComponent(c.voice)}`); } catch (e) { list = []; }
    }
    if (!list.length && v.default_voice) list = [{id: v.default_voice, name: v.default_voice}];
    const prev = sel.value;
    sel.innerHTML = list.map(x => `<option value="${esc(x.id)}">${esc(x.name)}</option>`).join("")
      || `<option value="">Default voice</option>`;
    if (list.some(x => x.id === prev)) sel.value = prev;
    else if (v.default_voice && list.some(x => x.id === v.default_voice)) sel.value = v.default_voice;
  }

  function render() {
    const c = choice();
    $("voiceBlock").classList.toggle("hidden", c.mode === "text");
    $("faceBlock").classList.toggle("hidden", c.mode !== "face");
    if (c.mode !== "text") $("voiceInfo").innerHTML = infoLine(catalog.voice[c.voice]);
    if (c.mode === "face") $("faceInfo").innerHTML = infoLine(catalog.face[c.face]);
    const probs = problems();
    if (probs.length) {
      $("mediaHelp").innerHTML = probs.map(x => x.problems.map(p => steps(x.kind, x.id, p)).join("")).join("") +
        `<button class="secondary" type="button" id="mediaRecheck">Check again</button>
         <span class="badge" style="margin-left:8px">Or choose a different option above, or <b>Text</b> to type instead.</span>`;
      $("mediaHelp").classList.remove("hidden");
      $("mediaRecheck").onclick = () => load(true);
    } else {
      $("mediaHelp").classList.add("hidden");
    }
    onChange();
  }

  async function load(keep) {
    const prev = keep && catalog ? {voice: $("voiceSvc").value, face: $("faceSvc").value} : null;
    catalog = await getJSON("/media");
    const opt = (kind) => Object.entries(catalog[kind]).map(([id, p]) =>
      `<option value="${esc(id)}">${esc(p.name)}${p.status.ready ? "" : " · needs setup"}</option>`).join("");
    $("voiceSvc").innerHTML = opt("voice");
    $("faceSvc").innerHTML = opt("face");
    if (prev) { $("voiceSvc").value = prev.voice; $("faceSvc").value = prev.face; }
    await loadVoices();
    render();
  }

  function initSetup(changed) {
    onChange = changed || (() => {});
    $("mediaSetup").innerHTML = `
      <label>Conversation</label>
      <div class="choice" id="convModes">
        <label><input type="radio" name="convMode" value="text" checked> Text</label>
        <label><input type="radio" name="convMode" value="voice"> Voice</label>
        <label><input type="radio" name="convMode" value="face"> Voice + face</label>
      </div>
      <div class="traits">Text: type your questions. Voice: talk to the witness and hear it answer. Voice + face: also see the witness's face react.</div>
      <div id="voiceBlock" class="hidden">
        <label for="voiceSvc">Voice service</label>
        <select id="voiceSvc"></select>
        <div class="traits" id="voiceInfo"></div>
        <label for="voiceId">Witness's voice</label>
        <div style="display:flex;gap:8px"><select id="voiceId"></select>
          <button class="secondary" type="button" id="voiceTest" style="white-space:nowrap">Hear it</button></div>
      </div>
      <div id="faceBlock" class="hidden">
        <label for="faceSvc">Face</label>
        <select id="faceSvc"></select>
        <div class="traits" id="faceInfo"></div>
      </div>
      <div id="mediaHelp" class="help hidden"></div>`;
    $("convModes").onchange = async () => { await loadVoices(); render(); };
    $("voiceSvc").onchange = async () => { await loadVoices(); render(); };
    $("faceSvc").onchange = render;
    $("voiceTest").onclick = () => {
      if (!ready() && problems().some(p => p.kind === "voice")) return;
      const c = choice();
      session = {...c};
      speakVoice("Hello. I was told to come and talk to you. What is this about?").catch(e => alert(e.message));
    };
    if ("speechSynthesis" in window) speechSynthesis.onvoiceschanged = () => loadVoices();
    return load(false);
  }

  // -------------------------------------------------------------------------
  // The free animated face
  // -------------------------------------------------------------------------

  // Per mood: brow tilt (+ = inner ends down, i.e. frowning), brow height, mouth
  // curve (+ smile / - frown), eye openness, and where the eyes look.
  const MOODS = {
    neutral:    {tilt: 0,   lift: 0,  curve: 0.05,  eye: 1.0,  look: [0, 0]},
    calm:       {tilt: -2,  lift: 1,  curve: 0.2,   eye: 0.8,  look: [0, 0]},
    friendly:   {tilt: -5,  lift: 4,  curve: 0.65,  eye: 0.9,  look: [0, 0]},
    confident:  {tilt: 4,   lift: 0,  curve: 0.3,   eye: 0.9,  look: [0, 0]},
    thoughtful: {tilt: -8,  lift: 3,  curve: -0.05, eye: 0.85, look: [-4, -4], asym: true},
    nervous:    {tilt: -12, lift: 5,  curve: -0.2,  eye: 1.15, look: [3, 1]},
    defensive:  {tilt: 10,  lift: -2, curve: -0.35, eye: 0.8,  look: [0, 0]},
    annoyed:    {tilt: 16,  lift: -4, curve: -0.5,  eye: 0.7,  look: [0, 0]},
    evasive:    {tilt: 3,   lift: 0,  curve: -0.1,  eye: 0.85, look: [6, 2]},
    surprised:  {tilt: -6,  lift: 9,  curve: 0,     eye: 1.3,  look: [0, 0], oh: true},
  };

  const face = {mood: "neutral", cur: {...MOODS.neutral}, open: 0, blink: 0, talkSource: null, raf: 0, el: null};

  function buildFace(container) {
    container.innerHTML = `
      <svg viewBox="0 0 200 220" class="face" role="img" aria-label="The witness's face">
        <ellipse cx="100" cy="112" rx="70" ry="88" fill="var(--face-skin)" stroke="var(--face-line)" stroke-width="2"/>
        <path d="M30 95 Q35 25 100 22 Q165 25 170 95 Q160 55 100 50 Q40 55 30 95Z" fill="var(--face-hair)"/>
        <g id="eyeL"><ellipse cx="72" cy="105" rx="13" ry="9" fill="#fff"/><circle id="pupL" cx="72" cy="105" r="5" fill="var(--face-line)"/>
          <rect id="lidL" x="57" y="94" width="30" height="0" fill="var(--face-skin)"/></g>
        <g id="eyeR"><ellipse cx="128" cy="105" rx="13" ry="9" fill="#fff"/><circle id="pupR" cx="128" cy="105" r="5" fill="var(--face-line)"/>
          <rect id="lidR" x="113" y="94" width="30" height="0" fill="var(--face-skin)"/></g>
        <path id="browL" d="M57 85 L87 85" stroke="var(--face-hair)" stroke-width="5" stroke-linecap="round"/>
        <path id="browR" d="M113 85 L143 85" stroke="var(--face-hair)" stroke-width="5" stroke-linecap="round"/>
        <path d="M100 112 Q96 135 100 140" fill="none" stroke="var(--face-line)" stroke-width="2" opacity=".5"/>
        <path id="mouth" d="" fill="var(--face-mouth)" stroke="var(--face-line)" stroke-width="2.5" stroke-linejoin="round"/>
      </svg>
      <div class="moodtag" id="moodTag"></div>`;
    face.el = container;
    cancelAnimationFrame(face.raf);
    const lerp = (a, b, t) => a + (b - a) * t;
    let nextBlink = performance.now() + 2500;
    const tick = (t) => {
      const target = MOODS[face.mood] || MOODS.neutral;
      for (const k of ["tilt", "lift", "curve", "eye"]) face.cur[k] = lerp(face.cur[k], target[k], 0.12);
      face.cur.look = [lerp(face.cur.look[0], target.look[0], 0.1), lerp(face.cur.look[1], target.look[1], 0.1)];
      // Blinking
      if (t > nextBlink) { face.blink = 1; nextBlink = t + 2500 + Math.random() * 3000; }
      face.blink = Math.max(0, face.blink - 0.15);
      // Mouth openness from the speaking source
      const target_open = face.talkSource ? face.talkSource(t) : 0;
      face.open = lerp(face.open, target_open, 0.35);
      drawFace(target);
      face.raf = requestAnimationFrame(tick);
    };
    face.raf = requestAnimationFrame(tick);
  }

  function drawFace(target) {
    const c = face.cur, q = (id) => face.el.querySelector("#" + id);
    if (!q("mouth")) return;
    const y = 85 - c.lift, tl = c.tilt * 0.6, asym = target.asym ? 6 : 0;
    q("browL").setAttribute("d", `M57 ${y - tl - asym} L87 ${y + tl - asym}`);
    q("browR").setAttribute("d", `M113 ${y + tl} L143 ${y - tl}`);
    // Lids droop for narrowed eyes (eye < 1) and close fully on a blink.
    const lid = (1 - Math.min(c.eye, 1)) * 11 + 20 * face.blink;
    for (const s of ["L", "R"]) {
      q("lid" + s).setAttribute("height", String(Math.min(20, Math.max(0, lid))));
      q("pup" + s).setAttribute("transform", `translate(${c.look[0]},${c.look[1]})`);
    }
    // Mouth: corners move with the curve; it opens while talking.
    const open = face.open * 16 + (target.oh ? 10 : 0);
    const w = target.oh ? 12 : 24, cy = 160, corner = cy - c.curve * 10;
    const mid = cy + c.curve * 10;
    q("mouth").setAttribute("d",
      `M${100 - w} ${corner} Q100 ${mid - open * 0.3} ${100 + w} ${corner} Q100 ${mid + open} ${100 - w} ${corner}Z`);
  }

  function setMood(mood) {
    face.mood = MOODS[mood] ? mood : "neutral";
    const tag = face.el?.querySelector("#moodTag");
    if (tag) tag.textContent = face.mood;
  }

  // Mouth movement for audio we can measure (natural voices) or can't (browser voice).
  function talkFromAudio(audioEl) {
    try {
      const ctx = talkFromAudio.ctx || (talkFromAudio.ctx = new AudioContext());
      ctx.resume();  // audio contexts start paused until the page has been clicked
      const src = ctx.createMediaElementSource(audioEl);
      const an = ctx.createAnalyser();
      an.fftSize = 512;
      src.connect(an); an.connect(ctx.destination);
      const buf = new Uint8Array(an.fftSize);
      face.talkSource = () => {
        an.getByteTimeDomainData(buf);
        let sum = 0;
        for (const v of buf) sum += (v - 128) ** 2;
        return Math.min(1, Math.sqrt(sum / buf.length) / 30);
      };
    } catch (e) {
      face.talkSource = talkSynthetic;
    }
  }
  const talkSynthetic = (t) => 0.35 + 0.35 * Math.abs(Math.sin(t / 90)) * (0.6 + 0.4 * Math.sin(t / 37));

  // -------------------------------------------------------------------------
  // Speaking
  // -------------------------------------------------------------------------

  function speakBrowser(text) {
    return new Promise((resolve) => {
      const u = new SpeechSynthesisUtterance(text);
      const v = speechSynthesis.getVoices().find(x => x.name === session.voice_id);
      if (v) u.voice = v;
      u.onstart = () => { face.talkSource = talkSynthetic; };
      u.onend = u.onerror = () => { face.talkSource = null; resolve(); };
      speechSynthesis.cancel();
      speechSynthesis.speak(u);
    });
  }

  async function speakServer(text) {
    const res = await fetch("/speech/synthesize", {method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({provider: session.voice, text, voice: session.voice_id})});
    if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || "Couldn't make the voice.");
    const url = URL.createObjectURL(await res.blob());
    const audio = new Audio(url);
    if (session.mode === "face" && session.face === "builtin") talkFromAudio(audio);
    await new Promise((resolve) => {
      audio.onended = audio.onerror = () => { face.talkSource = null; URL.revokeObjectURL(url); resolve(); };
      audio.play().catch(() => resolve());
    });
  }

  function speakVoice(text) {
    return session.voice === "browser" ? speakBrowser(text) : speakServer(text);
  }

  const estimateSeconds = (text) => Math.max(2, text.split(/\s+/).length / 2.6);
  const sleep = (s) => new Promise(r => setTimeout(r, s * 1000));

  async function speak(entry) {
    if (!session || session.mode === "text") return;
    if (session.mode === "face" && session.face === "builtin") setMood(entry.mood);
    if (session.mode === "face" && session.face !== "builtin") return avatar?.speak(entry.message);
    return speakVoice(entry.message);
  }

  // -------------------------------------------------------------------------
  // Listening
  // -------------------------------------------------------------------------

  // First call starts listening; the second call (clicking again) stops it.
  // Resolves with what was said, or "" if nothing was heard.
  function listen(onInterim) {
    if (recognizer) { recognizer.stop(); return null; }
    if (recorder) { recorder.stop(); return null; }
    if (session.voice === "browser") {
      return new Promise((resolve, reject) => {
        const r = recognizer = new SpeechRec();
        r.lang = "en-US"; r.interimResults = true; r.continuous = true;
        let final = "";
        r.onresult = (e) => {
          let interim = "";
          for (let i = e.resultIndex; i < e.results.length; i++) {
            if (e.results[i].isFinal) final += e.results[i][0].transcript + " ";
            else interim += e.results[i][0].transcript;
          }
          onInterim?.((final + interim).trim());
        };
        r.onerror = (e) => { recognizer = null; e.error === "no-speech" ? resolve("") : reject(new Error(`Speech recognition failed: ${e.error}`)); };
        r.onend = () => { recognizer = null; resolve(final.trim()); };
        r.start();
      });
    }
    return new Promise(async (resolve, reject) => {
      let stream;
      try { stream = await navigator.mediaDevices.getUserMedia({audio: true}); }
      catch (e) { return reject(new Error("Microphone access was blocked. Allow it in the browser's address bar.")); }
      const chunks = [];
      const rec = recorder = new MediaRecorder(stream);
      rec.ondataavailable = (e) => e.data.size && chunks.push(e.data);
      rec.onstop = async () => {
        recorder = null;
        stream.getTracks().forEach(t => t.stop());
        const blob = new Blob(chunks, {type: rec.mimeType || "audio/webm"});
        if (!blob.size) return resolve("");
        onInterim?.("Transcribing...");
        try {
          const res = await fetch(`/speech/transcribe?provider=${encodeURIComponent(session.voice)}`,
            {method: "POST", headers: {"Content-Type": blob.type}, body: blob});
          if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || "Transcription failed.");
          resolve((await res.json()).text || "");
        } catch (e) { reject(e); }
      };
      rec.start();
    });
  }

  const listening = () => Boolean(recognizer || recorder);

  // -------------------------------------------------------------------------
  // Lifelike avatars (browser half)
  // -------------------------------------------------------------------------

  function loadScript(src) {
    return new Promise((resolve, reject) => {
      if (document.querySelector(`script[src="${src}"]`)) return resolve();
      const s = document.createElement("script");
      s.src = src; s.crossOrigin = "anonymous"; s.onload = resolve;
      s.onerror = () => reject(new Error(`Couldn't load ${src}. Check your internet connection.`));
      document.head.appendChild(s);
    });
  }

  function videoStage(stage) {
    stage.innerHTML = `<video id="avatarVideo" autoplay playsinline class="avatar"></video><audio id="avatarAudio" autoplay></audio>`;
    return {video: $("avatarVideo"), audio: $("avatarAudio")};
  }

  const AVATARS = {
    // Simli lip-syncs to 16 kHz PCM audio from our own voice service.
    async simli(stage) {
      const {video, audio} = videoStage(stage);
      const {session_token} = await getJSON("/avatar/simli/start", {});
      const mod = await import("https://esm.sh/simli-client");
      const client = new mod.SimliClient(session_token, video, audio, null, mod.LogLevel?.INFO);
      await client.start();
      return {
        async speak(text) {
          const res = await fetch("/speech/synthesize", {method: "POST", headers: {"Content-Type": "application/json"},
            body: JSON.stringify({provider: session.voice, text, voice: session.voice_id, format: "pcm16"})});
          if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || "Couldn't make the voice.");
          const pcm = new Uint8Array(await res.arrayBuffer());
          for (let i = 0; i < pcm.length; i += 6000) client.sendAudioData(pcm.subarray(i, i + 6000));
          await sleep(pcm.length / 32000);  // 16 kHz x 2 bytes per sample
        },
        async stop() { await client.stop(); },
      };
    },

    // D-ID animates a photo over WebRTC; the server relays the handshake.
    async did(stage) {
      const {video} = videoStage(stage);
      const s = await getJSON("/avatar/did/start", {});
      const pc = new RTCPeerConnection({iceServers: s.ice_servers});
      pc.ontrack = (e) => { video.srcObject = e.streams[0]; };
      pc.onicecandidate = (e) => {
        if (e.candidate) getJSON("/avatar/did/ice", {id: s.id, session_id: s.session_id,
          candidate: e.candidate.candidate, sdpMid: e.candidate.sdpMid, sdpMLineIndex: e.candidate.sdpMLineIndex}).catch(() => {});
      };
      await pc.setRemoteDescription(s.offer);
      const answer = await pc.createAnswer();
      await pc.setLocalDescription(answer);
      await getJSON("/avatar/did/sdp", {id: s.id, session_id: s.session_id, answer: {type: answer.type, sdp: answer.sdp}});
      return {
        async speak(text) {
          const r = await getJSON("/avatar/did/speak", {id: s.id, session_id: s.session_id, text});
          await sleep((r.duration || estimateSeconds(text)) + 0.5);
        },
        async stop() { pc.close(); await getJSON("/avatar/did/stop", {id: s.id, session_id: s.session_id}).catch(() => {}); },
      };
    },

    // Tavus runs in a Daily video room; the app sends the witness's words as "echo" messages.
    async tavus(stage) {
      const {video, audio} = videoStage(stage);
      const s = await getJSON("/avatar/tavus/start", {});
      await loadScript("https://unpkg.com/@daily-co/daily-js");
      // Join without camera or microphone: the app does the listening itself.
      const call = window.Daily.createCallObject({audioSource: false, videoSource: false});
      call.on("track-started", (e) => {
        if (e.participant?.local) return;
        const stream = new MediaStream([e.track]);
        if (e.track.kind === "video") video.srcObject = stream; else audio.srcObject = stream;
      });
      await call.join({url: s.conversation_url});
      return {
        async speak(text) {
          call.sendAppMessage({message_type: "conversation", event_type: "conversation.echo",
            conversation_id: s.conversation_id, properties: {modality: "text", text, done: true}}, "*");
          await sleep(estimateSeconds(text) + 0.5);
        },
        async stop() { await call.leave().catch(() => {}); await getJSON("/avatar/tavus/stop", {conversation_id: s.conversation_id}); },
      };
    },

    // HeyGen's Streaming Avatar SDK (experimental: built from older documentation).
    async heygen(stage) {
      const {video} = videoStage(stage);
      const s = await getJSON("/avatar/heygen/start", {});
      if (!s.token) throw new Error("HeyGen didn't return a session token. Check HEYGEN_API_KEY.");
      const mod = await import("https://esm.sh/@heygen/streaming-avatar");
      const client = new mod.default({token: s.token});
      client.on(mod.StreamingEvents.STREAM_READY, (e) => { video.srcObject = e.detail; });
      await client.createStartAvatar({quality: mod.AvatarQuality?.Medium || "medium",
        ...(s.avatar_id ? {avatarName: s.avatar_id} : {})});
      return {
        async speak(text) {
          await client.speak({text, task_type: mod.TaskType?.REPEAT || "repeat"});
          await sleep(estimateSeconds(text));
        },
        async stop() { await client.stopAvatar().catch(() => {}); },
      };
    },
  };

  // -------------------------------------------------------------------------
  // Interview screen
  // -------------------------------------------------------------------------

  // Set up the interview screen. In voice modes a "Start the conversation" click
  // is needed first: browsers only allow sound after a click, and it connects avatars.
  function begin(data, onBegun, onSpoken) {
    session = data.media || {mode: "text"};
    const stage = $("stage"), beginBox = $("beginBox");
    $("talkBtn").classList.toggle("hidden", session.mode === "text");
    stage.classList.toggle("hidden", session.mode !== "face");
    beginBox.classList.toggle("hidden", session.mode === "text");
    if (session.mode === "face" && session.face === "builtin") buildFace(stage);
    if (session.mode === "face" && session.face !== "builtin")
      stage.innerHTML = `<div class="badge" style="padding:40px;text-align:center">The face appears when you start the conversation.</div>`;
    if (session.mode === "text") return onBegun?.();
    $("beginBtn").onclick = async () => {
      $("beginBtn").disabled = true;
      $("beginStatus").textContent = session.mode === "face" && session.face !== "builtin" ? "Connecting the face..." : "";
      try {
        if (session.mode === "face" && session.face !== "builtin") avatar = await AVATARS[session.face](stage);
        beginBox.classList.add("hidden");
        onBegun?.();
        const first = data.transcript[data.transcript.length - 1];
        if (first) await speak(first);
        onSpoken?.();
      } catch (e) {
        $("beginStatus").textContent = `Couldn't start: ${e.message}`;
        $("beginBtn").disabled = false;
      }
    };
  }

  async function stop() {
    if (recognizer) recognizer.abort();
    if (recorder) recorder.stop();
    if ("speechSynthesis" in window) speechSynthesis.cancel();
    if (avatar) { const a = avatar; avatar = null; await a.stop().catch(() => {}); }
    cancelAnimationFrame(face.raf);
  }
  window.addEventListener("pagehide", () => { if (avatar) stop(); });

  window.Media = {initSetup, choice, ready, begin, speak, listen, listening, stop, setMood};
})();
