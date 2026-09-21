"""
UI components and YouTube-style interactive closed-caption video/audio player.
"""

import base64
import json
from pathlib import Path
from typing import List, Dict, Any, Optional


def load_custom_css() -> str:
    """Return custom CSS for modern YouTube Studio Dark theme."""
    return """
<style>
/* Modern YouTube Studio Dark Theme */
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&family=Inter:wght@400;500;600;700&display=swap');

:root {
    --yt-red: #FF0000;
    --yt-red-hover: #CC0000;
    --yt-bg-dark: #0F0F0F;
    --yt-card-bg: #1F1F1F;
    --yt-card-border: #2D2D2D;
    --yt-text-primary: #F1F1F1;
    --yt-text-secondary: #AAAAAA;
    --yt-accent-blue: #3EA6FF;
    --yt-success: #2BA640;
    --yt-cc-bg: rgba(8, 8, 8, 0.85);
}

html, body, [class*="css"] {
    font-family: 'Roboto', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Main Container Styling */
.main .block-container {
    padding-top: 1.8rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

/* YouTube Header Bar */
.yt-header-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(135deg, rgba(255,0,0,0.15), rgba(255,0,0,0.05));
    border: 1px solid rgba(255,0,0,0.3);
    padding: 6px 14px;
    border-radius: 20px;
    color: #FF4E4E;
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.yt-main-title {
    font-size: 2.2rem;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.yt-main-title .yt-logo-icon {
    color: var(--yt-red);
    display: inline-block;
}

.yt-sub-title {
    color: var(--yt-text-secondary);
    font-size: 1.05rem;
    margin-bottom: 24px;
}

/* Feature Cards */
.yt-card {
    background: var(--yt-card-bg);
    border: 1px solid var(--yt-card-border);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.25);
    transition: border-color 0.2s ease;
}

.yt-card:hover {
    border-color: #3D3D3D;
}

.yt-card-title {
    font-size: 1.15rem;
    font-weight: 600;
    color: #FFFFFF;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Status Badges */
.yt-badge-success {
    background: rgba(43, 166, 64, 0.15);
    border: 1px solid rgba(43, 166, 64, 0.4);
    color: #4cd964;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
    display: inline-block;
}

.yt-badge-info {
    background: rgba(62, 166, 255, 0.15);
    border: 1px solid rgba(62, 166, 255, 0.4);
    color: #3EA6FF;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
    display: inline-block;
}

/* Primary Button Override */
button[kind="primary"] {
    background-color: var(--yt-red) !important;
    border-color: var(--yt-red) !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    padding: 0.55rem 1.4rem !important;
    transition: all 0.2s ease !important;
}

button[kind="primary"]:hover {
    background-color: var(--yt-red-hover) !important;
    border-color: var(--yt-red-hover) !important;
    box-shadow: 0 4px 12px rgba(255, 0, 0, 0.35) !important;
}

/* Metric Boxes */
div[data-testid="stMetricValue"] {
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
}
</style>
"""


def render_interactive_cc_player(
    media_path: str,
    segments: List[Dict[str, Any]],
    is_video: bool = True,
    vtt_content: str = "",
) -> str:
    """
    Generate an interactive HTML5/JS synchronized Closed Caption player.
    
    Features:
    - Real-time YouTube-style overlay subtitle directly inside the video viewport
    - Synchronized transcript cues that highlight as media plays
    - Click-to-seek: clicking any transcript line immediately seeks the player
    - CC Button: Toggle Closed Captions On/Off
    - Subtitle font size controls (+ / -)
    - Fullscreen & standard playback support
    """
    # Read media bytes into base64 data URI for embedded display
    with open(media_path, "rb") as f:
        media_bytes = f.read()
    media_b64 = base64.b64encode(media_bytes).decode("utf-8")
    
    suffix = Path(media_path).suffix.lower().replace(".", "")
    mime_type = f"video/{suffix}" if is_video else f"audio/{suffix}"
    if suffix == "mp3":
        mime_type = "audio/mpeg"
    elif suffix == "wav":
        mime_type = "audio/wav"
    elif suffix == "mkv":
        mime_type = "video/mp4"

    # Encode segments as JSON for the embedded JavaScript
    segments_json = json.dumps(segments, ensure_ascii=False)

    player_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    font-family: 'Roboto', 'Inter', sans-serif;
}}

body {{
    background: #0f0f0f;
    color: #f1f1f1;
    padding: 8px 0;
}}

.cc-studio-container {{
    display: grid;
    grid-template-columns: 1.3fr 1fr;
    gap: 16px;
    background: #181818;
    border: 1px solid #2b2b2b;
    border-radius: 14px;
    padding: 16px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.5);
}}

@media (max-width: 860px) {{
    .cc-studio-container {{
        grid-template-columns: 1fr;
    }}
}}

/* Left Column: Player & CC Overlay */
.player-column {{
    display: flex;
    flex-direction: column;
    gap: 10px;
}}

.video-wrapper {{
    position: relative;
    width: 100%;
    background: #000;
    border-radius: 10px;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 260px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.6);
}}

video, audio {{
    width: 100%;
    max-height: 420px;
    outline: none;
    border-radius: 10px;
}}

/* Audio Visualizer Canvas if Audio file */
.audio-card-view {{
    width: 100%;
    padding: 24px;
    display: flex;
    flex-direction: column;
    align-items: center;
    background: linear-gradient(180deg, #1e1e1e 0%, #121212 100%);
    border-radius: 10px;
}}

.audio-icon-pulse {{
    font-size: 48px;
    color: #ff0000;
    margin-bottom: 12px;
    animation: pulse 2s infinite ease-in-out;
}}

@keyframes pulse {{
    0% {{ transform: scale(1); opacity: 0.8; }}
    50% {{ transform: scale(1.1); opacity: 1; }}
    100% {{ transform: scale(1); opacity: 0.8; }}
}}

/* YouTube Style Closed Caption Overlay */
.yt-cc-overlay {{
    position: absolute;
    bottom: 54px;
    left: 50%;
    transform: translateX(-50%);
    width: 88%;
    text-align: center;
    pointer-events: none;
    z-index: 10;
    transition: opacity 0.15s ease;
}}

.yt-cc-text {{
    display: inline-block;
    background: rgba(8, 8, 8, 0.88);
    color: #ffffff;
    font-size: 19px;
    font-weight: 500;
    line-height: 1.4;
    padding: 6px 14px;
    border-radius: 4px;
    text-shadow: 0px 1px 2px rgba(0,0,0,0.8);
    box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    transition: all 0.12s ease;
}}

.yt-cc-text:empty {{
    display: none;
}}

/* Controls Toolbar */
.player-controls-bar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #222222;
    padding: 8px 14px;
    border-radius: 8px;
    font-size: 0.85rem;
    color: #aaa;
}}

.controls-left, .controls-right {{
    display: flex;
    align-items: center;
    gap: 10px;
}}

.cc-toggle-btn {{
    background: #333333;
    border: 1px solid #444;
    color: #ffffff;
    padding: 4px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 700;
    font-size: 0.8rem;
    letter-spacing: 0.5px;
    transition: all 0.2s ease;
}}

.cc-toggle-btn.active {{
    background: #ff0000;
    border-color: #ff0000;
    color: #ffffff;
    box-shadow: 0 0 8px rgba(255,0,0,0.5);
}}

.size-btn {{
    background: #2d2d2d;
    border: 1px solid #444;
    color: #fff;
    width: 26px;
    height: 26px;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}}

.size-btn:hover {{
    background: #444;
}}

/* Right Column: Interactive Transcript List */
.transcript-column {{
    display: flex;
    flex-direction: column;
    height: 460px;
    background: #1f1f1f;
    border: 1px solid #2a2a2a;
    border-radius: 10px;
    overflow: hidden;
}}

.transcript-header {{
    padding: 12px 16px;
    background: #252525;
    border-bottom: 1px solid #333;
    display: flex;
    align-items: center;
    justify-content: space-between;
}}

.transcript-title {{
    font-size: 0.95rem;
    font-weight: 600;
    color: #fff;
    display: flex;
    align-items: center;
    gap: 8px;
}}

.live-indicator {{
    width: 8px;
    height: 8px;
    background: #ff0000;
    border-radius: 50%;
    box-shadow: 0 0 6px #ff0000;
}}

.transcript-list {{
    flex: 1;
    overflow-y: auto;
    padding: 8px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    scroll-behavior: smooth;
}}

.transcript-list::-webkit-scrollbar {{
    width: 6px;
}}

.transcript-list::-webkit-scrollbar-thumb {{
    background: #3d3d3d;
    border-radius: 3px;
}}

.transcript-cue {{
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 8px 10px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.15s ease;
    border-left: 3px solid transparent;
}}

.transcript-cue:hover {{
    background: #2c2c2c;
}}

.transcript-cue.active {{
    background: rgba(255, 0, 0, 0.12);
    border-left: 3px solid #ff0000;
}}

.cue-time {{
    background: #2d2d2d;
    color: #3ea6ff;
    font-family: monospace;
    font-size: 0.75rem;
    padding: 2px 6px;
    border-radius: 4px;
    white-space: nowrap;
    font-weight: 600;
}}

.transcript-cue.active .cue-time {{
    background: #ff0000;
    color: #ffffff;
}}

.cue-text {{
    color: #d1d1d1;
    font-size: 0.88rem;
    line-height: 1.4;
}}

.transcript-cue.active .cue-text {{
    color: #ffffff;
    font-weight: 600;
}}
</style>
</head>
<body>

<div class="cc-studio-container">
    <!-- Left Column: Video & YouTube Closed Caption Overlay -->
    <div class="player-column">
        <div class="video-wrapper">
            {'<video id="mediaPlayer" controls playsinline src="data:' + mime_type + ';base64,' + media_b64 + '"></video>' if is_video else '<div class="audio-card-view"><div class="audio-icon-pulse">&#9835;</div><audio id="mediaPlayer" controls style="width:100%" src="data:' + mime_type + ';base64,' + media_b64 + '"></audio></div>'}
            
            <div id="ytCcOverlay" class="yt-cc-overlay">
                <span id="ytCcText" class="yt-cc-text"></span>
            </div>
        </div>

        <div class="player-controls-bar">
            <div class="controls-left">
                <button id="ccToggleBtn" class="cc-toggle-btn active" title="Toggle Closed Captions (C)">CC [ON]</button>
                <span style="font-size:0.75rem; color:#888;">Auto-sync active</span>
            </div>
            <div class="controls-right">
                <span>Font:</span>
                <button id="fontSizeDec" class="size-btn" title="Decrease font size">-</button>
                <button id="fontSizeInc" class="size-btn" title="Increase font size">+</button>
            </div>
        </div>
    </div>

    <!-- Right Column: Interactive Transcript with Click-to-Seek -->
    <div class="transcript-column">
        <div class="transcript-header">
            <div class="transcript-title">
                <span class="live-indicator"></span>
                <span>Interactive Transcript</span>
            </div>
            <span style="font-size: 0.75rem; color: #888;">Click line to seek</span>
        </div>

        <div id="transcriptList" class="transcript-list">
            <!-- Rendered by JavaScript -->
        </div>
    </div>
</div>

<script>
const segments = {segments_json};
let ccEnabled = true;
let currentFontSize = 19;
let activeIndex = -1;

const media = document.getElementById("mediaPlayer");
const ccOverlay = document.getElementById("ytCcOverlay");
const ccText = document.getElementById("ytCcText");
const ccToggleBtn = document.getElementById("ccToggleBtn");
const transcriptList = document.getElementById("transcriptList");
const fontIncBtn = document.getElementById("fontSizeInc");
const fontDecBtn = document.getElementById("fontSizeDec");

function formatTime(secs) {{
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${{m.toString().padStart(2, '0')}}:${{s.toString().padStart(2, '0')}}`;
}}

// Populate Transcript List
function renderTranscript() {{
    transcriptList.innerHTML = "";
    segments.forEach((seg, idx) => {{
        const item = document.createElement("div");
        item.className = "transcript-cue";
        item.id = `cue-${{idx}}`;
        item.innerHTML = `
            <span class="cue-time">${{formatTime(seg.start)}}</span>
            <span class="cue-text">${{seg.text}}</span>
        `;
        item.addEventListener("click", () => {{
            media.currentTime = seg.start + 0.05;
            media.play();
        }});
        transcriptList.appendChild(item);
    }});
}}

renderTranscript();

// Timeupdate event handler for real-time CC sync
media.addEventListener("timeupdate", () => {{
    const ct = media.currentTime;
    let foundIdx = -1;
    let currentText = "";

    for (let i = 0; i < segments.length; i++) {{
        if (ct >= segments[i].start && ct <= segments[i].end) {{
            foundIdx = i;
            currentText = segments[i].text;
            break;
        }}
    }}

    // Update Overlay
    if (ccEnabled && currentText) {{
        ccText.textContent = currentText;
        ccText.style.display = "inline-block";
    }} else {{
        ccText.textContent = "";
        ccText.style.display = "none";
    }}

    // Update Transcript Highlight & Auto-scroll
    if (foundIdx !== activeIndex) {{
        if (activeIndex !== -1) {{
            const prev = document.getElementById(`cue-${{activeIndex}}`);
            if (prev) prev.classList.remove("active");
        }}
        activeIndex = foundIdx;
        if (activeIndex !== -1) {{
            const current = document.getElementById(`cue-${{activeIndex}}`);
            if (current) {{
                current.classList.add("active");
                current.scrollIntoView({{ behavior: "smooth", block: "nearest" }});
            }}
        }}
    }}
}});

// Toggle CC
ccToggleBtn.addEventListener("click", () => {{
    ccEnabled = !ccEnabled;
    if (ccEnabled) {{
        ccToggleBtn.classList.add("active");
        ccToggleBtn.textContent = "CC [ON]";
    }} else {{
        ccToggleBtn.classList.remove("active");
        ccToggleBtn.textContent = "CC [OFF]";
        ccText.textContent = "";
        ccText.style.display = "none";
    }}
}});

// Font size adjusters
fontIncBtn.addEventListener("click", () => {{
    if (currentFontSize < 32) {{
        currentFontSize += 2;
        ccText.style.fontSize = currentFontSize + "px";
    }}
}});

fontDecBtn.addEventListener("click", () => {{
    if (currentFontSize > 12) {{
        currentFontSize -= 2;
        ccText.style.fontSize = currentFontSize + "px";
    }}
}});

// Keyboard shortcut: Press 'c' to toggle CC
window.addEventListener("keydown", (e) => {{
    if (e.target.tagName !== "INPUT" && e.target.tagName !== "TEXTAREA") {{
        if (e.key === "c" || e.key === "C") {{
            ccToggleBtn.click();
        }}
    }}
}});
</script>

</body>
</html>
"""
    return player_html
