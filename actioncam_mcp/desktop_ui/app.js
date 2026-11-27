/**
 * ActionCam MCP Desktop Application Logic
 * Communicates with the local ActionCam MCP HTTP Server and DaVinci Resolve Studio.
 */

document.addEventListener("DOMContentLoaded", () => {
  const API_BASE = "";

  // State
  let currentBlueprint = null;
  let scannedAssets = [];
  let selectedExportProfile = "youtube_4k";

  // Elements
  const resolveStatusPill = document.getElementById("resolve-status-pill");
  const resolveStatusText = document.getElementById("resolve-status-text");
  const btnLaunchResolve = document.getElementById("btn-launch-resolve");
  const consoleOutput = document.getElementById("console-output");
  const btnClearConsole = document.getElementById("btn-clear-console");

  // Tab switching
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabPanes = document.querySelectorAll(".tab-pane");

  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      tabBtns.forEach(b => b.classList.remove("active"));
      tabPanes.forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      const target = btn.getAttribute("data-tab");
      document.getElementById(target).classList.add("active");
    });
  });

  // Logging utility
  function log(message, type = "info") {
    const time = new Date().toLocaleTimeString();
    const entry = document.createElement("div");
    entry.className = `log-entry log-${type}`;
    entry.textContent = `[${time}] ${message}`;
    consoleOutput.appendChild(entry);
    consoleOutput.scrollTop = consoleOutput.scrollHeight;
  }

  btnClearConsole.addEventListener("click", () => {
    consoleOutput.innerHTML = "";
  });

  // 1. Live DaVinci Resolve Status Check
  async function checkResolveStatus() {
    try {
      const res = await fetch(`${API_BASE}/api/status`);
      if (res.ok) {
        const data = await res.json();
        if (data.connected) {
          resolveStatusPill.className = "status-pill status-connected";
          resolveStatusText.textContent = `DaVinci Resolve Connected (v${data.version}) — Project: ${data.project || 'Untitled'}`;
          btnLaunchResolve.style.display = "none";
        } else {
          resolveStatusPill.className = "status-pill status-disconnected";
          resolveStatusText.textContent = "DaVinci Resolve Offline (External Scripting)";
          if (data.resolve_exe_exists) {
            btnLaunchResolve.style.display = "inline-flex";
          }
        }
      }
    } catch (err) {
      resolveStatusPill.className = "status-pill status-disconnected";
      resolveStatusText.textContent = "MCP Backend Server Offline";
    }
  }

  setInterval(checkResolveStatus, 3000);
  checkResolveStatus();

  btnLaunchResolve.addEventListener("click", async () => {
    log("Attempting to launch DaVinci Resolve Studio...", "info");
    try {
      const res = await fetch(`${API_BASE}/api/launch-resolve`, { method: "POST" });
      const data = await res.json();
      log(data.status || data.error, data.error ? "error" : "success");
    } catch (err) {
      log(`Launch failed: ${err.message}`, "error");
    }
  });

  // 2. Scan Directory
  const btnScanMedia = document.getElementById("btn-scan-media");
  const inputSourceDir = document.getElementById("input-source-dir");
  const mediaListContainer = document.getElementById("media-list");
  const assetCountBadge = document.getElementById("asset-count-badge");

  btnScanMedia.addEventListener("click", async () => {
    const sourceDir = inputSourceDir.value.trim();
    if (!sourceDir) return alert("Please enter a source directory.");

    log(`Scanning media in ${sourceDir}...`, "info");
    try {
      const res = await fetch(`${API_BASE}/api/scan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source_dir: sourceDir }),
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);

      scannedAssets = data.assets || [];
      assetCountBadge.textContent = `${scannedAssets.length} clips found`;
      renderAssetList(scannedAssets);
      log(`Found ${scannedAssets.length} assets (${scannedAssets.filter(a => a.is_slowmo).length} slow-mo clips).`, "success");
    } catch (err) {
      log(`Scan error: ${err.message}`, "error");
    }
  });

  function renderAssetList(assets) {
    if (!assets || assets.length === 0) {
      mediaListContainer.innerHTML = '<div class="empty-state">No media files found in specified path.</div>';
      return;
    }
    mediaListContainer.innerHTML = "";
    assets.forEach(asset => {
      const item = document.createElement("div");
      item.className = "asset-item";
      let badgeHtml = "";
      if (asset.is_slowmo) {
        badgeHtml = `<span class="badge badge-slowmo">${asset.fps || 120}fps SlowMo</span>`;
      } else if (asset.type === "video") {
        badgeHtml = `<span class="badge badge-realtime">${asset.fps || 25}fps Realtime</span>`;
      } else {
        badgeHtml = `<span class="badge">Audio</span>`;
      }

      item.innerHTML = `
        <span><strong>${asset.name}</strong> <small class="text-dim">(${asset.size_mb} MB${asset.duration_sec ? ', ' + asset.duration_sec + 's' : ''})</small></span>
        <div>${badgeHtml}</div>
      `;
      mediaListContainer.appendChild(item);
    });
  }

  // 3. Auto-Organize Files & Bins
  const btnOrganizeFiles = document.getElementById("btn-organize-files");
  const inputProjectDir = document.getElementById("input-project-dir");
  const selectOrgMode = document.getElementById("select-org-mode");

  btnOrganizeFiles.addEventListener("click", async () => {
    const sourceDir = inputSourceDir.value.trim();
    const projectDir = inputProjectDir.value.trim();
    const mode = selectOrgMode.value;

    log(`Organizing assets into structured project folder: ${projectDir}...`, "info");
    try {
      const res = await fetch(`${API_BASE}/api/organize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source_dir: sourceDir, project_dir: projectDir, mode }),
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);

      log(`Organization complete! Realtime: ${data.organized.realtime}, SlowMo: ${data.organized.slowmo}, Audio: ${data.organized.audio}`, "success");
      alert("Files and project structure organized successfully!");
    } catch (err) {
      log(`Organization failed: ${err.message}`, "error");
    }
  });

  // 4. Custom LUT Toggle
  const selectLut = document.getElementById("select-lut");
  const customLutGroup = document.getElementById("custom-lut-group");

  selectLut.addEventListener("change", () => {
    customLutGroup.style.display = selectLut.value === "custom" ? "block" : "none";
  });

  // 5. Decode Reference Video
  const btnDecodeRef = document.getElementById("btn-decode-ref");
  const inputRefPath = document.getElementById("input-ref-path");
  const blueprintSummary = document.getElementById("blueprint-summary");
  const statDuration = document.getElementById("stat-duration");
  const statShots = document.getElementById("stat-shots");
  const statAvgShot = document.getElementById("stat-avg-shot");
  const statPacing = document.getElementById("stat-pacing");
  const timelineVisualizer = document.getElementById("timeline-visualizer");
  const shotsTbody = document.getElementById("shots-tbody");

  btnDecodeRef.addEventListener("click", async () => {
    const refPath = inputRefPath.value.trim();
    if (!refPath) return alert("Please specify reference video path.");

    log(`Decoding reference edit: ${refPath}...`, "info");
    try {
      const res = await fetch(`${API_BASE}/api/decode-reference`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reference_path: refPath, fps: 25.0 }),
      });
      const blueprint = await res.json();
      if (blueprint.error) throw new Error(blueprint.error);

      currentBlueprint = blueprint;
      renderBlueprint(blueprint);
      log(`Decoded ${blueprint.shot_count} shots from reference video! Total duration: ${blueprint.total_duration_sec}s.`, "success");
    } catch (err) {
      log(`Decode failed: ${err.message}`, "error");
    }
  });

  function renderBlueprint(bp) {
    blueprintSummary.style.display = "grid";
    statDuration.textContent = `${bp.total_duration_sec}s`;
    statShots.textContent = bp.shot_count;
    const avg = bp.shot_count > 0 ? (bp.total_duration_sec / bp.shot_count).toFixed(2) : "0";
    statAvgShot.textContent = `${avg}s`;
    statPacing.textContent = bp.pacing_style.replace("_", " ").toUpperCase();

    // Visualizer ribbon
    timelineVisualizer.innerHTML = "";
    bp.shots.forEach(s => {
      const block = document.createElement("div");
      let paceClass = "cut-medium";
      if (s.pacing === "fast_action") paceClass = "cut-fast";
      if (s.pacing === "establishing_wide") paceClass = "cut-wide";

      block.className = `timeline-cut-block ${paceClass}`;
      const widthPercent = Math.max(3, (s.duration_sec / bp.total_duration_sec) * 100);
      block.style.width = `${widthPercent}%`;
      block.title = `Shot #${s.shot_index}: ${s.duration_sec}s (${s.pacing})`;
      block.textContent = `#${s.shot_index}`;
      timelineVisualizer.appendChild(block);
    });

    // Table
    shotsTbody.innerHTML = "";
    bp.shots.forEach(s => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong>#${s.shot_index}</strong></td>
        <td>${s.start_frame}</td>
        <td>${s.end_frame}</td>
        <td>${s.duration_sec}s</td>
        <td><span class="badge ${s.pacing === 'fast_action' ? 'badge-slowmo' : 'badge-realtime'}">${s.pacing}</span></td>
        <td><code>${s.suggested_vfx}</code></td>
        <td><small>${s.audio_cue}</small></td>
      `;
      shotsTbody.appendChild(tr);
    });
  }

  // 6. Match Cuts Preview & Assembly
  const btnPreviewMatches = document.getElementById("btn-preview-matches");
  const btnAssembleResolve = document.getElementById("btn-assemble-resolve");
  const inputTimelineName = document.getElementById("input-timeline-name");
  const matchesTbody = document.getElementById("matches-tbody");

  btnPreviewMatches.addEventListener("click", async () => {
    const refPath = inputRefPath.value.trim();
    const sourceDir = inputSourceDir.value.trim();
    const camPreset = document.getElementById("select-camera-preset").value;
    const lutPath = selectLut.value === "custom" ? document.getElementById("input-custom-lut").value : selectLut.value;

    log("Matching source clips to decoded reference cuts...", "info");
    try {
      const res = await fetch(`${API_BASE}/api/match-cuts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          reference_path: refPath,
          source_dir: sourceDir,
          camera_preset: camPreset,
          custom_lut_path: lutPath,
        }),
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);

      renderMatchTable(data.matched_shots);
      log(`Generated match blueprint for ${data.matched_shots.length} shots!`, "success");
    } catch (err) {
      log(`Matching failed: ${err.message}`, "error");
    }
  });

  function renderMatchTable(matches) {
    matchesTbody.innerHTML = "";
    matches.forEach(m => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong>#${m.shot_index}</strong></td>
        <td>${m.record_frame} - ${m.record_end_frame}</td>
        <td><span title="${m.clip_path}">${m.clip_name}</span></td>
        <td>${m.source_start_frame} &rarr; ${m.source_end_frame}</td>
        <td><span class="badge ${m.speed_multiplier < 1 ? 'badge-slowmo' : ''}">${(m.speed_multiplier * 100).toFixed(0)}%</span></td>
        <td><small>${m.lut_path || 'Rec.709'}</small></td>
      `;
      matchesTbody.appendChild(tr);
    });
  }

  btnAssembleResolve.addEventListener("click", async () => {
    const tlName = inputTimelineName.value.trim();
    const refPath = inputRefPath.value.trim();
    const sourceDir = inputSourceDir.value.trim();
    const camPreset = document.getElementById("select-camera-preset").value;
    const lutPath = selectLut.value === "custom" ? document.getElementById("input-custom-lut").value : selectLut.value;
    const bgmPath = document.getElementById("input-bgm-path").value.trim();

    log(`Assembling timeline '${tlName}' in DaVinci Resolve Studio...`, "info");
    try {
      const res = await fetch(`${API_BASE}/api/assemble`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          timeline_name: tlName,
          reference_path: refPath,
          source_dir: sourceDir,
          camera_preset: camPreset,
          custom_lut_path: lutPath,
          bgm_path: bgmPath,
        }),
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);

      if (data.resolve_assembled) {
        log(`Timeline '${tlName}' assembled live in DaVinci Resolve! (${data.shots_assembled} clips)`, "success");
        alert(`Success! Timeline '${tlName}' assembled in DaVinci Resolve Studio.`);
      } else {
        log(`DaVinci Resolve not connected. Generated FCPXML interchange file at: ${data.fcpxml_path}`, "warning");
        alert(`DaVinci Resolve is offline. FCPXML 1.9 file created at:\n${data.fcpxml_path}\nImport via File > Import > Timeline in DaVinci Resolve.`);
      }
    } catch (err) {
      log(`Assembly error: ${err.message}`, "error");
    }
  });

  // 7. Deliver & Export Presets
  const presetCards = document.querySelectorAll(".preset-card");
  presetCards.forEach(card => {
    card.addEventListener("click", () => {
      presetCards.forEach(c => c.classList.remove("active"));
      card.classList.add("active");
      selectedExportProfile = card.getAttribute("data-profile");
    });
  });

  const btnQueueExport = document.getElementById("btn-queue-export");
  const btnStartRender = document.getElementById("btn-start-render");
  const exportStatusBox = document.getElementById("export-status-box");

  async function handleExport(startNow) {
    const outDir = document.getElementById("input-export-dir").value.trim();
    const prefix = document.getElementById("input-export-prefix").value.trim();

    log(`Configuring export render job for profile: ${selectedExportProfile}...`, "info");
    try {
      const res = await fetch(`${API_BASE}/api/export`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          output_dir: outDir,
          filename_prefix: prefix,
          profile: selectedExportProfile,
          start_render_now: startNow,
        }),
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);

      exportStatusBox.innerHTML = `
        <div class="export-job-item">
          <h4>${data.profile_name}</h4>
          <p><strong>Target:</strong> ${data.target_dir}/${data.filename}</p>
          <p><strong>Status:</strong> ${data.status} ${data.job_id ? '(Job ID: ' + data.job_id + ')' : ''}</p>
        </div>
      `;
      log(`Export configured: ${data.status}`, "success");
    } catch (err) {
      log(`Export failed: ${err.message}`, "error");
    }
  }

  btnQueueExport.addEventListener("click", () => handleExport(false));
  btnStartRender.addEventListener("click", () => handleExport(true));

  // 8. Quick Run Full Workflow
  const btnQuickRun = document.getElementById("btn-quick-run");
  btnQuickRun.addEventListener("click", async () => {
    if (!confirm("Run end-to-end workflow: Ingest -> Decode Ref -> Match Cuts -> Assemble Timeline -> Queue Export?")) return;

    log("Executing full automated workflow...", "info");
    try {
      const res = await fetch(`${API_BASE}/api/assemble`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          timeline_name: "ActionCam_Master_Edit",
          reference_path: inputRefPath.value.trim(),
          source_dir: inputSourceDir.value.trim(),
          camera_preset: document.getElementById("select-camera-preset").value,
        }),
      });
      const data = await res.json();
      log(`Full workflow complete! Assembled ${data.shots_assembled} shots into timeline.`, "success");
      alert("Full workflow executed successfully!");
    } catch (err) {
      log(`Full workflow error: ${err.message}`, "error");
    }
  });
});

