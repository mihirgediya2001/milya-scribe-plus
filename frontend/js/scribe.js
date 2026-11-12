document.addEventListener("DOMContentLoaded", () => {
  if (!API.getToken()) { window.location.href = "/login"; return; }
  populateNavbar();
  initScribe();
});


function populateNavbar() {
  const user = API.getUser();
  if (!user) return;
  const el = document.getElementById("navUser");
  if (el) {
    el.innerHTML = `
      <span class="clinic-badge">${user.clinic_name}</span>
      <span class="role-badge">${user.role}</span>
      <span class="user-name">${user.name}</span>
      <button class="btn btn-ghost btn-sm" id="logoutBtn">Logout</button>
    `;
    document.getElementById("logoutBtn").addEventListener("click", () => {
      API.clearAuth();
      window.location.href = "/login";
    });
  }
}


let state = {
  sessionId: null,
  transcript: "",
  mediaRecorder: null,
  isRecording: false,
  chunks: [],
  questions: [],
  currentQuestionIdx: 0,
  replyRecorder: null,
  isReplyRecording: false,
  replyChunks: [],
};


function initScribe() {
  document.getElementById("recordBtn").addEventListener("click", toggleRecording);
  document.getElementById("sendTextBtn").addEventListener("click", () => {
    handleTextInput(document.getElementById("textInput"));
  });
  document.getElementById("textInput").addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleTextInput(document.getElementById("textInput"));
    }
  });
  document.getElementById("finalizeBtn").addEventListener("click", handleFinalize);
  document.getElementById("copyBtn").addEventListener("click", handleCopy);
  document.getElementById("clearBtn").addEventListener("click", handleClear);
  document.getElementById("replyForm").addEventListener("submit", (e) => {
    e.preventDefault();
    handleReply();
  });
  document.getElementById("replyRecordBtn").addEventListener("click", toggleReplyRecording);
  document.getElementById("skipQuestionBtn").addEventListener("click", skipQuestion);

  checkPermissions();

  const params = new URLSearchParams(window.location.search);
  const resumeId = params.get("session");
  if (resumeId) loadSession(resumeId);
}


function checkPermissions() {
  const user = API.getUser();
  if (!user) return;
  const canFinalize = ["admin", "dentist"].includes(user.role);
  if (!canFinalize) {
    document.getElementById("finalizeBtn").style.display = "none";
  }
}


async function loadSession(sessionId) {
  setStatus("thinking", "Loading session...");
  try {
    const res = await API.getSession(sessionId);
    state.sessionId = res.id;
    state.transcript = res.transcript;

    const box = document.getElementById("transcriptBox");
    box.innerHTML = "";
    const lines = res.transcript.split("\n").filter(l => l.trim());
    for (const line of lines) {
      const match = line.match(/^\[(\w+)\]:\s*(.+)$/);
      if (match) {
        const role = match[1].toLowerCase();
        const text = match[2];
        const div = document.createElement("div");
        div.className = `turn ${role === "agent" ? "agent" : ""}`;
        div.innerHTML = `<span class="role">${role}</span>${escapeHtml(text)}`;
        box.appendChild(div);
      }
    }
    box.scrollTop = box.scrollHeight;

    if (res.note_rendered) updateNote(res.note_rendered);

    await runAnalysis();
  } catch (err) {
    setStatus("idle", `Could not load session: ${err.message}`);
  }
}


/* Recording (main input) */

async function toggleRecording() {
  if (state.isRecording) stopRecording();
  else await startRecording();
}

async function startRecording() {
  const btn = document.getElementById("recordBtn");
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    state.mediaRecorder = new MediaRecorder(stream, { mimeType: getMimeType() });
    state.chunks = [];
    state.mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) state.chunks.push(e.data);
    };
    state.mediaRecorder.onstop = async () => {
      stream.getTracks().forEach((t) => t.stop());
      const blob = new Blob(state.chunks, { type: state.mediaRecorder.mimeType });
      await handleAudioBlob(blob);
    };
    state.mediaRecorder.start();
    state.isRecording = true;
    btn.textContent = "⏹";
    btn.classList.add("active");
    setStatus("recording", "Recording... speak now.");
  } catch {
    setStatus("idle", "Microphone access denied. Please allow mic access.");
  }
}

function stopRecording() {
  const btn = document.getElementById("recordBtn");
  if (state.mediaRecorder && state.mediaRecorder.state !== "inactive") {
    state.mediaRecorder.stop();
  }
  state.isRecording = false;
  btn.textContent = "🎙";
  btn.classList.remove("active");
  setStatus("thinking", "Transcribing audio...");
}

function getMimeType() {
  if (MediaRecorder.isTypeSupported("audio/webm;codecs=opus")) return "audio/webm;codecs=opus";
  if (MediaRecorder.isTypeSupported("audio/webm")) return "audio/webm";
  if (MediaRecorder.isTypeSupported("audio/mp4")) return "audio/mp4";
  return "";
}


/* Recording for clarifying question replies */

async function toggleReplyRecording() {
  if (state.isReplyRecording) stopReplyRecording();
  else await startReplyRecording();
}

async function startReplyRecording() {
  const btn = document.getElementById("replyRecordBtn");
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    state.replyRecorder = new MediaRecorder(stream, { mimeType: getMimeType() });
    state.replyChunks = [];
    state.replyRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) state.replyChunks.push(e.data);
    };
    state.replyRecorder.onstop = async () => {
      stream.getTracks().forEach((t) => t.stop());
      const blob = new Blob(state.replyChunks, { type: state.replyRecorder.mimeType });
      await handleReplyAudioBlob(blob);
    };
    state.replyRecorder.start();
    state.isReplyRecording = true;
    btn.textContent = "⏹";
    btn.classList.add("active");
    setStatus("recording", "Recording your answer...");
  } catch {
    setStatus("idle", "Microphone access denied.");
  }
}

function stopReplyRecording() {
  const btn = document.getElementById("replyRecordBtn");
  if (state.replyRecorder && state.replyRecorder.state !== "inactive") {
    state.replyRecorder.stop();
  }
  state.isReplyRecording = false;
  btn.textContent = "🎙";
  btn.classList.remove("active");
  setStatus("thinking", "Transcribing your answer...");
}

async function handleReplyAudioBlob(blob) {
  const formData = new FormData();
  formData.append("audio", blob, "reply.webm");
  try {
    const res = await API.transcribe(formData);
    if (res.text) {
      document.getElementById("replyInput").value = res.text;
      handleReply();
    } else {
      setStatus("idle", "No speech detected. Try again.");
    }
  } catch (err) {
    setStatus("idle", `Transcription error: ${err.message}`);
  }
}


/* Handle inputs */

async function handleAudioBlob(blob) {
  const formData = new FormData();
  formData.append("audio", blob, "recording.webm");
  try {
    const res = await API.transcribe(formData);
    if (res.text) {
      addToTranscript("patient", res.text);
      await runAnalysis();
    } else {
      setStatus("idle", "No speech detected. Try again.");
    }
  } catch (err) {
    setStatus("idle", `Transcription error: ${err.message}`);
  }
}

function handleTextInput(textarea) {
  const text = textarea.value.trim();
  if (!text) return;
  textarea.value = "";
  addToTranscript("patient", text);
  runAnalysis();
}

async function handleReply() {
  const input = document.getElementById("replyInput");
  const text = input.value.trim();
  if (!text) return;
  input.value = "";

  const q = state.questions[state.currentQuestionIdx];
  if (q) addToTranscript("agent", q.question);
  addToTranscript("patient", text);

  state.currentQuestionIdx++;
  if (state.currentQuestionIdx < state.questions.length) {
    showCurrentQuestion();
  } else {
    await runAnalysis();
  }
}

function skipQuestion() {
  state.currentQuestionIdx++;
  if (state.currentQuestionIdx < state.questions.length) {
    showCurrentQuestion();
  } else {
    hideQuestions();
    if (state.transcript.trim()) {
      runAnalysis();
    } else {
      setStatus("idle", "Questions skipped. You can add more details or finalize.");
    }
  }
}


/* Transcript */

function addToTranscript(role, text) {
  state.transcript += `\n[${role.toUpperCase()}]: ${text}`;
  state.transcript = state.transcript.trim();

  const box = document.getElementById("transcriptBox");
  const placeholder = box.querySelector(".placeholder");
  if (placeholder) placeholder.remove();

  const div = document.createElement("div");
  div.className = `turn ${role === "agent" ? "agent" : ""}`;
  div.innerHTML = `<span class="role">${role}</span>${escapeHtml(text)}`;
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}


/* Analysis loop */

async function runAnalysis() {
  setStatus("thinking", "Analyzing transcript...");
  try {
    const res = await API.analyze({
      transcript: state.transcript,
      session_id: state.sessionId,
    });

    state.sessionId = res.session_id;
    if (res.session_title) updateSessionTitle(res.session_title);
    updateTemplateFields(res.template_fields);
    updateNote(res.rendered_note);
    updateSuggestions(res.ai_suggestions);

    if (res.is_complete) {
      hideQuestions();
      setStatus("done", "All required fields are covered. You can finalize the note.");
    } else if (res.clarifying_questions && res.clarifying_questions.length > 0) {
      state.questions = res.clarifying_questions;
      state.currentQuestionIdx = 0;
      showCurrentQuestion();
      document.getElementById("questionsBox").classList.remove("hidden");
      setStatus("idle", "Answer the question below, or skip to finalize.");
    } else {
      hideQuestions();
      setStatus("idle", "Add more details or finalize the note.");
    }
  } catch (err) {
    setStatus("idle", `Analysis error: ${err.message}`);
  }
}


/* Finalize */

async function handleFinalize() {
  if (!state.sessionId) {
    setStatus("idle", "Nothing to finalize yet. Record or type a complaint first.");
    return;
  }
  setStatus("thinking", "Generating final note...");
  try {
    const res = await API.finalize({ session_id: state.sessionId });
    updateNote(res.rendered_note);
    setStatus("done", "Note finalized and saved. You can copy it to your PMS.");
    document.getElementById("copyBtn").disabled = false;
    hideQuestions();
  } catch (err) {
    setStatus("idle", `Finalize error: ${err.message}`);
  }
}


/* UI updaters */

function setStatus(type, message) {
  const el = document.getElementById("statusBar");
  el.className = `status-bar ${type}`;
  el.textContent = message;
}

function updateTemplateFields(fields) {
  const list = document.getElementById("fieldList");
  const progress = document.getElementById("progressText");
  list.innerHTML = "";
  let filled = 0;
  for (const f of fields) {
    if (f.status === "filled") filled++;
    const li = document.createElement("li");
    li.className = `field-item ${f.status}`;
    li.innerHTML = `
      <span class="field-name">${f.label}</span>
      <span>${f.value || "---"}</span>
    `;
    list.appendChild(li);
  }
  progress.textContent = `${filled} / ${fields.length} fields`;
}

function updateNote(rendered) {
  document.getElementById("noteOutput").textContent = rendered || "Note will appear here.";
}

function updateSessionTitle(title) {
  document.title = `${title} - Milya Scribe Plus`;
}

function updateSuggestions(suggestions) {
  const user = API.getUser();
  if (!user || !["admin", "dentist"].includes(user.role)) return;

  const box = document.getElementById("suggestionsBox");
  const dxGroup = document.getElementById("diagnosisList");
  const dxItems = document.getElementById("diagnosisItems");
  const nsGroup = document.getElementById("nextStepsList");
  const nsItems = document.getElementById("nextStepsItems");

  if (!suggestions) { box.classList.add("hidden"); return; }

  const dx = suggestions.differential_diagnoses || [];
  const ns = suggestions.recommended_next_steps || [];

  if (dx.length === 0 && ns.length === 0) { box.classList.add("hidden"); return; }

  box.classList.remove("hidden");

  if (dx.length > 0) {
    dxGroup.classList.remove("hidden");
    dxItems.innerHTML = dx.map(d => `<li>${escapeHtml(d)}</li>`).join("");
  } else {
    dxGroup.classList.add("hidden");
  }

  if (ns.length > 0) {
    nsGroup.classList.remove("hidden");
    nsItems.innerHTML = ns.map(n => `<li>${escapeHtml(n)}</li>`).join("");
  } else {
    nsGroup.classList.add("hidden");
  }
}

function showCurrentQuestion() {
  const q = state.questions[state.currentQuestionIdx];
  if (!q) { hideQuestions(); return; }

  document.getElementById("currentQuestion").textContent = q.question;
  document.getElementById("questionProgress").textContent =
    `Question ${state.currentQuestionIdx + 1} of ${state.questions.length}`;
  document.getElementById("questionsBox").classList.remove("hidden");
  document.getElementById("replyInput").focus();
}

function hideQuestions() {
  document.getElementById("questionsBox").classList.add("hidden");
}

function handleCopy() {
  const text = document.getElementById("noteOutput").textContent;
  navigator.clipboard.writeText(text).then(() => {
    const btn = document.getElementById("copyBtn");
    const orig = btn.textContent;
    btn.textContent = "Copied!";
    setTimeout(() => { btn.textContent = orig; }, 1500);
  });
}

function handleClear() {
  state = {
    sessionId: null, transcript: "", mediaRecorder: null, isRecording: false,
    chunks: [], questions: [], currentQuestionIdx: 0, replyRecorder: null,
    isReplyRecording: false, replyChunks: [],
  };
  document.getElementById("transcriptBox").innerHTML =
    '<p class="placeholder">Your conversation will appear here.</p>';
  document.getElementById("fieldList").innerHTML = "";
  document.getElementById("progressText").textContent = "0 / 10 fields";
  document.getElementById("noteOutput").textContent = "Note will appear here.";
  document.getElementById("copyBtn").disabled = true;
  document.getElementById("suggestionsBox").classList.add("hidden");
  hideQuestions();
  document.title = "Scribe Session - Milya Scribe Plus";
  setStatus("idle", "Ready. Record or type the patient's complaint.");
  window.history.replaceState(null, "", "/scribe");
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
