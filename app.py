import streamlit as st
import yt_dlp
import os

st.set_page_config(page_title="Media Downloader Hub", layout="centered")

# ---------- UI HEADER ----------
st.markdown("""
# 🎬 Media Downloader Hub

### 🚀 Download videos from YouTube, Instagram & more  
✨ Choose quality | 📦 See file size | ⚡ Fast downloads  

---
""")

# ---------- PLATFORM SELECT ----------
platform = st.selectbox(
    "🌐 Select Platform",
    ["Auto Detect", "YouTube", "Instagram", "Facebook", "Twitter (X)", "Other"]
)

# ---------- INPUT ----------
col1, col2 = st.columns([3, 1])

with col1:
    url = st.text_input("🔗 Paste your video link here")

with col2:
    st.write("")
    st.write("")
    fetch_clicked = st.button("🔍 Fetch")

# ---------- DOWNLOAD FOLDER ----------
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# ---------- SESSION ----------
if "formats" not in st.session_state:
    st.session_state.formats = {}

if "info" not in st.session_state:
    st.session_state.info = None

# ---------- SIZE FORMAT ----------
def format_size(size):
    if size:
        return f"{round(size / (1024*1024), 2)} MB"
    return "Unknown"

# ---------- FETCH FORMATS ----------
def get_video_formats(url):
    ydl_opts = {'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    formats = {}

    for f in info['formats']:
        if f.get('height') and f.get('ext') == 'mp4':
            size = f.get('filesize') or f.get('filesize_approx')
            label = f"{f['height']}p - {format_size(size)}"
            formats[label] = f['height']

    return info, formats

# ---------- PROGRESS ----------
progress_bar = st.progress(0)
status_text = st.empty()

def progress_hook(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded = d.get('downloaded_bytes', 0)

        if total:
            percent = int(downloaded * 100 / total)
            progress_bar.progress(percent)
            status_text.text(f"⚡ Downloading... {percent}%")

    elif d['status'] == 'finished':
        progress_bar.progress(100)
        status_text.text("✅ Download complete!")

# ---------- DOWNLOAD FUNCTION ----------
def download_media(url, selected_height, is_audio=False):

    if is_audio:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
            'progress_hooks': [progress_hook]
        }

    else:
        ydl_opts = {
            # 🔥 FIXED AUDIO + COMPATIBILITY
            'format': f"bestvideo[height<={selected_height}][vcodec^=avc1]+bestaudio[acodec^=mp4a]/best[height<={selected_height}]",
            'merge_output_format': 'mp4',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'progress_hooks': [progress_hook]
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

        if is_audio:
            filename = os.path.splitext(filename)[0] + ".mp3"

    return filename

# ---------- FETCH INFO ----------
if fetch_clicked:
    if url:
        try:
            info, formats = get_video_formats(url)

            st.session_state.info = info
            st.session_state.formats = formats

            # Thumbnail (with fallback)
            thumbnail = info.get('thumbnail')

            if thumbnail:
                st.image(thumbnail)
            else:
                st.warning("⚠️ Thumbnail not available for this platform")

            st.subheader(info.get('title', "No Title"))

            st.success("✅ Video info loaded!")

        except Exception as e:
            st.error(f"❌ Error: {e}")

# ---------- OPTIONS ----------
if st.session_state.formats:

    st.markdown("## ⚙️ Download Settings")

    col1, col2 = st.columns(2)

    with col1:
        quality = st.selectbox(
            "🎯 Select Quality",
            list(st.session_state.formats.keys())
        )

    with col2:
        download_type = st.radio(
            "📦 Format",
            ["🎬 Video (MP4)", "🎵 Audio (MP3)"]
        )

    selected_height = st.session_state.formats[quality]

    st.markdown("---")

    # ---------- DOWNLOAD ----------
    if st.button("⬇️ Download Now", use_container_width=True):
        with st.spinner("🚀 Processing your request..."):
            try:
                is_audio = download_type == "🎵 Audio (MP3)"

                file_path = download_media(url, selected_height, is_audio)

                st.success("🎉 Download completed!")
                st.balloons()

                with open(file_path, "rb") as f:
                    st.download_button(
                        "📥 Download File",
                        data=f,
                        file_name=os.path.basename(file_path)
                    )

            except Exception as e:
                st.error(f"❌ Error: {e}")

# ---------- FOOTER ----------
st.markdown("---")
st.caption("⚡ Built with Streamlit | Multi-platform support | Hackathon Ready 🚀")
