"""
YouTube-Style Closed Caption & Video Subtitle Generator System
Production-ready application for automatic multilingual audio extraction, timestamped transcription,
synchronized CC playback, subtitle editing, and multi-format exports.
"""

import os
import tempfile
import time
from pathlib import Path

try:
    import pandas as pd
except Exception:
    pd = None

import streamlit as st
import streamlit.components.v1 as components


# Import modular backend
from src.audio_processor import extract_audio, get_media_info, is_ffmpeg_available
from src.speech_to_text import (
    AVAILABLE_MODELS,
    LANGUAGE_OPTIONS,
    get_device,
    load_whisper_model,
    transcribe_audio,
)
from src.subtitle_generator import (
    format_time_display,
    generate_json_transcript,
    generate_plain_text,
    generate_srt,
    generate_vtt,
)
from src.ui_components import load_custom_css, render_interactive_cc_player
from src.video_processor import burn_subtitles_to_video

# ---------------------------------------------------------
# Streamlit Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="CC Studio - Video & Audio Subtitle Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject Custom Theme Styling
st.markdown(load_custom_css(), unsafe_allow_html=True)


# ---------------------------------------------------------
# Cached Whisper Model Loader
# ---------------------------------------------------------
@st.cache_resource(show_spinner=False)
def get_cached_whisper_model(model_name: str):
    """Load and cache Whisper model in memory."""
    return load_whisper_model(model_name)


# ---------------------------------------------------------
# Sidebar Controls & System Status
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ CC Engine Settings")

    model_name = st.selectbox(
        "Whisper ASR Model",
        options=AVAILABLE_MODELS,
        index=1,  # Default to 'base'
        help="Tiny/Base are ultra fast. Small/Medium provide higher accuracy for regional dialects.",
    )

    selected_lang_label = st.selectbox(
        "Audio Spoken Language",
        options=list(LANGUAGE_OPTIONS.keys()),
        index=0,
        help="Select language for higher accuracy or leave as Auto-Detect.",
    )
    language_code = LANGUAGE_OPTIONS[selected_lang_label]

    task_type = st.radio(
        "Generation Task",
        options=["Transcribe (Original Language CC)", "Translate (Translate to English CC)"],
        index=0,
    )
    whisper_task = "transcribe" if "Transcribe" in task_type else "translate"

    st.markdown("---")
    st.markdown("### 🖥️ System Status")
    
    device_name = get_device().upper()
    ffmpeg_ok = is_ffmpeg_available()
    
    st.markdown(
        f"""
        <div style="background:#1c1c1c; padding:10px; border-radius:8px; border:1px solid #2e2e2e; font-size:0.85rem;">
            <div>⚡ <b>Compute Device:</b> <span style="color:#3ea6ff;">{device_name}</span></div>
            <div style="margin-top:4px;">🎥 <b>FFmpeg Engine:</b> <span style="color:{'#2ba640' if ffmpeg_ok else '#ff4e4e'};">{'Active' if ffmpeg_ok else 'Not Detected'}</span></div>
            <div style="margin-top:4px;">🌐 <b>Engine:</b> <span style="color:#aaa;">OpenAI Whisper ({model_name})</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.75rem; color:#777;'>Closed Caption Subtitle Generator • Production Ready</div>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# Main App Header
# ---------------------------------------------------------
st.markdown(
    """
    <div class="yt-header-badge">🎬 Closed Caption Studio</div>
    <div class="yt-main-title">
        <span class="yt-logo-icon">▶</span> YouTube-Style Closed Caption & Subtitle Generator
    </div>
    <div class="yt-sub-title">
        Upload any gallery video or audio file to automatically generate synchronized closed captions, interactive timestamps, and professional subtitle files (.srt, .vtt, .json).
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Upload Section
# ---------------------------------------------------------
upload_col, info_col = st.columns([2, 1])

with upload_col:
    uploaded_file = st.file_uploader(
        "Choose a Video or Audio File",
        type=["mp4", "mkv", "mov", "avi", "webm", "wav", "mp3", "m4a", "flac", "ogg", "aac"],
        help="Upload gallery video or audio files in any standard format.",
    )

with info_col:
    if uploaded_file:
        st.markdown(
            f"""
            <div class="yt-card" style="padding:14px; margin-top:28px;">
                <div style="font-size:0.9rem; font-weight:600; color:#fff;">📁 Uploaded File Details</div>
                <div style="font-size:0.82rem; color:#aaa; margin-top:6px;"><b>Name:</b> {uploaded_file.name}</div>
                <div style="font-size:0.82rem; color:#aaa;"><b>Size:</b> {round(uploaded_file.size / (1024*1024), 2)} MB</div>
                <div style="font-size:0.82rem; color:#aaa;"><b>Type:</b> {uploaded_file.type or 'Media'}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Initialize Session State
if "transcription_data" not in st.session_state:
    st.session_state.transcription_data = None
if "current_file_name" not in st.session_state:
    st.session_state.current_file_name = None
if "saved_media_path" not in st.session_state:
    st.session_state.saved_media_path = None
if "is_video" not in st.session_state:
    st.session_state.is_video = False

# Reset state when a new file is uploaded
if uploaded_file and uploaded_file.name != st.session_state.current_file_name:
    st.session_state.transcription_data = None
    st.session_state.current_file_name = uploaded_file.name
    
    # Save uploaded media to a temporary file
    temp_dir = tempfile.gettempdir()
    file_ext = Path(uploaded_file.name).suffix
    saved_path = os.path.join(temp_dir, f"cc_studio_upload_{int(time.time())}{file_ext}")
    with open(saved_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.session_state.saved_media_path = saved_path
    video_exts = {".mp4", ".mkv", ".mov", ".avi", ".webm"}
    st.session_state.is_video = file_ext.lower() in video_exts

# ---------------------------------------------------------
# Action Button: Generate Closed Captions
# ---------------------------------------------------------
if uploaded_file and st.session_state.saved_media_path:
    col_btn, col_hint = st.columns([1, 2])
    with col_btn:
        generate_clicked = st.button("✨ Generate Closed Captions", type="primary", use_container_width=True)
    with col_hint:
        st.markdown(
            f"<div style='color:#888; font-size:0.85rem; padding-top:8px;'>Using <b>{model_name}</b> model • Target: <b>{selected_lang_label}</b></div>",
            unsafe_allow_html=True,
        )

    if generate_clicked:
        progress_bar = st.progress(0, text="Initializing CC Studio...")
        status_placeholder = st.empty()

        try:
            # Step 1: Extract 16kHz audio
            progress_bar.progress(20, text="Extracting and preparing clean 16kHz audio...")
            extracted_audio_path = extract_audio(st.session_state.saved_media_path)
            
            # Step 2: Load Whisper Model
            progress_bar.progress(40, text=f"Loading Whisper '{model_name}' ASR model ({device_name})...")
            model = get_cached_whisper_model(model_name)
            
            # Step 3: Perform Speech Recognition
            progress_bar.progress(60, text="Transcribing speech and aligning timecode segments...")
            start_time = time.time()
            transcription = transcribe_audio(
                model=model,
                audio_path=extracted_audio_path,
                language=language_code,
                task=whisper_task,
            )
            elapsed_time = round(time.time() - start_time, 2)
            
            progress_bar.progress(90, text="Formatting WebVTT & SubRip captions...")
            
            # Step 4: Generate formats
            srt_content = generate_srt(transcription["segments"])
            vtt_content = generate_vtt(transcription["segments"])
            plain_text = generate_plain_text(transcription["segments"])
            json_content = generate_json_transcript(
                transcription["segments"],
                metadata={
                    "file_name": uploaded_file.name,
                    "model": model_name,
                    "language": transcription["language"],
                    "elapsed_seconds": elapsed_time,
                }
            )

            # Store in session state
            st.session_state.transcription_data = {
                "text": transcription["text"],
                "segments": transcription["segments"],
                "language": transcription["language"],
                "elapsed_time": elapsed_time,
                "srt": srt_content,
                "vtt": vtt_content,
                "txt": plain_text,
                "json": json_content,
            }
            
            progress_bar.progress(100, text="Done!")
            time.sleep(0.5)
            progress_bar.empty()
            st.success(f"🎉 Closed Captions generated successfully in {elapsed_time}s! (Detected Language: {transcription['language'].upper()})")

        except Exception as e:
            progress_bar.empty()
            st.error(f"Error during transcription: {str(e)}")

# ---------------------------------------------------------
# Output Presentation & Interactive Player
# ---------------------------------------------------------
if st.session_state.transcription_data:
    data = st.session_state.transcription_data
    segments = data["segments"]

    st.markdown("---")
    
    # Overview Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Segments", f"{len(segments)} cues")
    with m2:
        st.metric("Total Words", f"{len(data['txt'].split())} words")
    with m3:
        st.metric("Detected Language", data["language"].upper())
    with m4:
        st.metric("Inference Time", f"{data['elapsed_time']}s")

    # 1. YouTube-Style Synchronized Closed Caption Player
    st.markdown("### 📺 Synchronized YouTube-Style Closed Caption Player")
    st.caption("Play the media to watch real-time subtitle sync. Click on any line in the transcript to jump immediately to that point in the video.")

    player_html = render_interactive_cc_player(
        media_path=st.session_state.saved_media_path,
        segments=segments,
        is_video=st.session_state.is_video,
        vtt_content=data["vtt"],
    )
    components.html(player_html, height=520, scrolling=False)

    # 2. Subtitle Editor & Fine-Tuning
    st.markdown("### ✏️ Subtitle Segment Editor & Inspector")
    with st.expander("Review / Edit Subtitle Cues & Timestamps", expanded=False):
        df_segments = pd.DataFrame([
            {
                "ID": s["id"],
                "Start (s)": round(s["start"], 2),
                "End (s)": round(s["end"], 2),
                "Start Time": format_time_display(s["start"]),
                "End Time": format_time_display(s["end"]),
                "Caption Text": s["text"],
            }
            for s in segments
        ])

        edited_df = st.data_editor(
            df_segments,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "Caption Text": st.column_config.TextColumn("Caption Text", width="large"),
            },
        )

        if st.button("💾 Apply Edits & Re-generate Subtitles"):
            updated_segments = []
            for _, row in edited_df.iterrows():
                updated_segments.append({
                    "id": int(row["ID"]),
                    "start": float(row["Start (s)"]),
                    "end": float(row["End (s)"]),
                    "text": str(row["Caption Text"]).strip(),
                })
            
            st.session_state.transcription_data["segments"] = updated_segments
            st.session_state.transcription_data["srt"] = generate_srt(updated_segments)
            st.session_state.transcription_data["vtt"] = generate_vtt(updated_segments)
            st.session_state.transcription_data["txt"] = generate_plain_text(updated_segments)
            st.session_state.transcription_data["json"] = generate_json_transcript(updated_segments)
            st.rerun()

    # 3. Export Hub
    st.markdown("### 📥 Download & Export Subtitles")
    base_name = Path(uploaded_file.name).stem

    exp_c1, exp_c2, exp_c3, exp_c4 = st.columns(4)
    with exp_c1:
        st.download_button(
            label="📄 Download SubRip (.SRT)",
            data=data["srt"],
            file_name=f"{base_name}_subtitles.srt",
            mime="text/plain",
            use_container_width=True,
        )
    with exp_c2:
        st.download_button(
            label="🌐 Download WebVTT (.VTT)",
            data=data["vtt"],
            file_name=f"{base_name}_captions.vtt",
            mime="text/vtt",
            use_container_width=True,
        )
    with exp_c3:
        st.download_button(
            label="📝 Download Plain Text (.TXT)",
            data=data["txt"],
            file_name=f"{base_name}_transcript.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with exp_c4:
        st.download_button(
            label="📊 Download JSON (.JSON)",
            data=data["json"],
            file_name=f"{base_name}_captions.json",
            mime="application/json",
            use_container_width=True,
        )

    # 4. Burn-in Subtitles to Video
    if st.session_state.is_video and ffmpeg_ok:
        st.markdown("---")
        st.markdown("### 🔥 Hardsub / Burn-in Subtitles to Video")
        st.caption("Permanently embed YouTube-style subtitles into the video frames so it can be played anywhere without a separate subtitle file.")

        burn_col1, burn_col2 = st.columns([1, 2])
        with burn_col1:
            font_size_choice = st.slider("Subtitle Font Size", min_value=12, max_value=32, value=18, step=1)
            burn_btn = st.button("🎬 Render Hardcoded Subtitle Video", type="secondary", use_container_width=True)

        if burn_btn:
            with st.spinner("Rendering subtitled video via FFmpeg..."):
                try:
                    # Save current SRT to temp file
                    temp_dir = tempfile.gettempdir()
                    temp_srt_path = os.path.join(temp_dir, f"{base_name}_temp.srt")
                    with open(temp_srt_path, "w", encoding="utf-8") as srt_file:
                        srt_file.write(data["srt"])

                    captioned_video_path = burn_subtitles_to_video(
                        video_path=st.session_state.saved_media_path,
                        srt_path=temp_srt_path,
                        font_size=font_size_choice,
                    )

                    with open(captioned_video_path, "rb") as vid_file:
                        vid_bytes = vid_file.read()

                    st.success("🎉 Video rendered successfully with hardcoded closed captions!")
                    st.download_button(
                        label="⬇️ Download Captioned Video (.MP4)",
                        data=vid_bytes,
                        file_name=f"{base_name}_with_subtitles.mp4",
                        mime="video/mp4",
                    )
                except Exception as burn_err:
                    st.error(f"Failed to burn subtitles into video: {burn_err}")
