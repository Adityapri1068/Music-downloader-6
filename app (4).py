
import streamlit as st
import yt_dlp
from PIL import Image
import requests
from io import BytesIO
import os

st.set_page_config(page_title="🎧 Music & Video Downloader", page_icon="🎧")
st.title("🎧 Music & Video Downloader")

st.markdown("### 🔎 Search YouTube or Paste a Video/Playlist URL")

search_mode = st.radio("Select Mode", ["🔍 Keyword Search", "📎 Paste URL"])

download_dir = "downloads"
os.makedirs(download_dir, exist_ok=True)

url = ""
search_clicked = False

if search_mode == "🔍 Keyword Search":
    keyword = st.text_input("Enter search term (e.g., lofi chill mix)")
    if st.button("🔍 Search"):
        try:
            st.markdown("#### Top Search Results:")
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                search_results = ydl.extract_info(f"ytsearch10:{keyword}", download=False)["entries"]
                for idx, entry in enumerate(search_results):
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        st.image(entry["thumbnail"], width=100)
                    with col2:
                        st.markdown(f"**{entry['title']}**")
                        if st.button("Download this", key=f"select_{idx}"):
                            url = f"https://www.youtube.com/watch?v={entry['id']}"
                            search_clicked = True
                            break
        except Exception as e:
            st.error("❌ Failed to search YouTube. Please try again.")

elif search_mode == "📎 Paste URL":
    col1, col2 = st.columns([4, 1])
    with col1:
        url = st.text_input("Paste YouTube URL", label_visibility="collapsed", placeholder="Video or Playlist URL")
    with col2:
        search_clicked = st.button("🔍")

# Proceed with download logic if a URL is selected or pasted
if url and search_clicked:
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        st.error("❌ This video/playlist is unavailable or restricted. Please try another.")
        st.stop()

    try:
        is_playlist = '_type' in info and info['_type'] == 'playlist'

        if is_playlist:
            st.markdown(f"### 📃 Playlist: {info['title']} ({len(info['entries'])} videos)")
            for idx, entry in enumerate(info['entries']):
                st.markdown(f"**{idx+1}. {entry['title']}**")
                if st.button("Download Video", key=f"pl_dl_{idx}"):
                    single_url = entry['url']
                    ydl_opts = {
                        'format': '18',
                        'outtmpl': os.path.join(download_dir, f"{entry['title']}.mp4"),
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl_inner:
                        ydl_inner.download([single_url])
                    st.success("Downloaded successfully!")
        else:
            title = info.get('title')
            thumbnail_url = info.get('thumbnail')
            formats = info.get('formats', [])

            st.success(f"Found: **{title}**")
            if thumbnail_url:
                response = requests.get(thumbnail_url)
                img = Image.open(BytesIO(response.content))
                st.image(img, caption="Thumbnail", use_column_width=True)

            quality_options = []
            quality_format_map = {}

            for f in formats:
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                    label = f"{f.get('format_id')} - {f.get('height')}p"
                    quality_options.append(label)
                    quality_format_map[label] = f.get('format_id')

            format_choice = st.radio("Download type", ['Audio (.webm)', 'Video (.mp4)', 'Thumbnail'])

            if format_choice == 'Video (.mp4)' and quality_options:
                selected_quality = st.selectbox("Select Quality", quality_options)
                selected_format_id = quality_format_map[selected_quality]
            else:
                selected_format_id = None

            if st.button("Download"):
                if format_choice == 'Audio (.webm)':
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'outtmpl': os.path.join(download_dir, f'{title}.webm'),
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                    st.success("Audio downloaded successfully!")
                    st.audio(os.path.join(download_dir, f'{title}.webm'))

                elif format_choice == 'Video (.mp4)' and selected_format_id:
                    ydl_opts = {
                        'format': selected_format_id,
                        'outtmpl': os.path.join(download_dir, f'{title}.mp4'),
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                    st.success("Video downloaded successfully!")
                    st.video(os.path.join(download_dir, f'{title}.mp4'))

                elif format_choice == 'Thumbnail':
                    image_path = os.path.join(download_dir, f'{title}_thumbnail.jpg')
                    img.save(image_path)
                    st.success("Thumbnail image saved!")
                    st.image(image_path, caption="Saved Thumbnail")
    except Exception as e:
        st.error("⚠️ An error occurred while processing the video. Please try another.")
