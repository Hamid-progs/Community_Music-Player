import streamlit as st
import os
import json
import uuid

# File paths for storage
SONGS_FILE = "songs.json"
PLAYLISTS_FILE = "playlists.json"

# Ensure files exist
if not os.path.exists(SONGS_FILE):
    with open(SONGS_FILE, "w") as f:
        json.dump([], f)

if not os.path.exists(PLAYLISTS_FILE):
    with open(PLAYLISTS_FILE, "w") as f:
        json.dump({}, f)

# Load songs
def load_songs():
    with open(SONGS_FILE, "r") as f:
        return json.load(f)

# Save songs
def save_songs(songs):
    with open(SONGS_FILE, "w") as f:
        json.dump(songs, f, indent=4)

# Load playlists
def load_playlists():
    with open(PLAYLISTS_FILE, "r") as f:
        return json.load(f)

# Save playlists
def save_playlists(playlists):
    with open(PLAYLISTS_FILE, "w") as f:
        json.dump(playlists, f, indent=4)

# Add new song
def add_song(title, artist, file):
    songs = load_songs()
    song_id = str(uuid.uuid4())
    file_path = os.path.join("uploads", f"{song_id}_{file.name}")

    os.makedirs("uploads", exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(file.read())

    songs.append({
        "id": song_id,
        "title": title,
        "artist": artist,
        "file_path": file_path,
        "likes": 0
    })
    save_songs(songs)

# Like a song
def like_song(song_id):
    songs = load_songs()
    for song in songs:
        if song["id"] == song_id:
            song["likes"] += 1
            break
    save_songs(songs)

# Add song to playlist
def add_to_playlist(song_id, playlist_name):
    playlists = load_playlists()
    if playlist_name not in playlists:
        playlists[playlist_name] = []
    if song_id not in playlists[playlist_name]:
        playlists[playlist_name].append(song_id)
    save_playlists(playlists)

# Create new playlist
def create_playlist(name):
    playlists = load_playlists()
    if name not in playlists:
        playlists[name] = []
        save_playlists(playlists)
        return True
    return False

# ------------------- UI -------------------
st.title("🎵 Community Music Player")

menu = st.sidebar.radio("Menu", ["Upload Song", "Songs", "Playlists"])

# -------- Upload Song + Create Playlist --------
if menu == "Upload Song":
    st.header("Upload a New Song")
    title = st.text_input("Song Title")
    artist = st.text_input("Artist")
    file = st.file_uploader("Upload Audio File", type=["mp3", "wav", "ogg"])

    if st.button("Upload"):
        if title and artist and file:
            add_song(title, artist, file)
            st.success(f"Uploaded: {title} by {artist}")
        else:
            st.error("Please fill all fields and upload a file.")

    st.divider()
    st.header("Create a New Playlist")
    new_playlist = st.text_input("Playlist Name")
    if st.button("Create Playlist"):
        if new_playlist:
            if create_playlist(new_playlist):
                st.success(f"Playlist '{new_playlist}' created!")
            else:
                st.warning("Playlist already exists.")
        else:
            st.error("Please enter a playlist name.")

# -------- Songs Section --------
elif menu == "Songs":
    st.header("🎶 All Songs")
    if st.button("🔄 Refresh Songs"):
        st.rerun()  # ✅ FIXED

    songs = load_songs()
    playlists = load_playlists()

    search = st.text_input("🔍 Search Songs by Title or Artist")

    # Filter songs
    if search:
        songs = [s for s in songs if search.lower() in s["title"].lower() or search.lower() in s["artist"].lower()]

    if not songs:
        st.info("No songs found.")
    else:
        for song in songs:
            st.subheader(f"{song['title']} - {song['artist']}")
            st.audio(song["file_path"])

            col1, col2, col3 = st.columns(3)
            if col1.button(f"👍 Like ({song['likes']})", key=f"like_{song['id']}"):
                like_song(song["id"])
                st.rerun()  # ✅ FIXED

            if playlists:
                choice = col2.selectbox("Add to Playlist", list(playlists.keys()), key=f"pl_{song['id']}")
                if col3.button("Add", key=f"add_{song['id']}"):
                    add_to_playlist(song["id"], choice)
                    st.success(f"Added {song['title']} to {choice}")
                    st.rerun()  # ✅ FIXED
            else:
                col2.info("No playlists available. Create one first.")

# -------- Playlists Section --------
elif menu == "Playlists":
    st.header("🎼 Playlists")
    if st.button("🔄 Refresh Playlists"):
        st.rerun()  # ✅ FIXED

    playlists = load_playlists()
    songs = load_songs()
    song_dict = {s["id"]: s for s in songs}

    # 🔍 Search playlists
    playlist_search = st.text_input("🔍 Search Playlists by Name")
    if playlist_search:
        playlists = {k: v for k, v in playlists.items() if playlist_search.lower() in k.lower()}

    if not playlists:
        st.info("No playlists created yet.")
    else:
        for name, song_ids in playlists.items():
            st.subheader(f"📂 {name}")
            for sid in song_ids:
                if sid in song_dict:
                    song = song_dict[sid]
                    st.text(f"{song['title']} - {song['artist']}")
                    st.audio(song["file_path"])
