import streamlit as st
import subprocess
import os
import re
import imageio_ffmpeg as im_ffmpeg

# বড় ফাইল আপলোডের জন্য সাইজ লিমিট ২০০০ MB করা হলো
st._config.set_option("server.maxUploadSize", 2000)

st.set_page_config(page_title="Smart Video Editor Pro", page_icon="🎬", layout="centered")

st.title("🎬 Anti-Copyright Master Video Engine (Audio Sync Fix)")
st.write("সুজন ভাই, এই কোডটিতে থাম্বনেইল ২ সেকেন্ড করা হয়েছে এবং অডিও আগে চলে যাওয়ার সমস্যাটি ফিক্স করা হয়েছে।")

# অস্থায়ী ফাইল ট্র্যাকিং পাথসমূহ
v_start = "temp_0_input.mp4"
v_step1 = "temp_1_copyright_free.mp4"
v_step2 = "temp_2_cropped.mp4"
v_final = "final_perfect_video.mp4"

# সেশন স্টেট ইনিশিয়েলাইজেশন
if "step" not in st.session_state:
    st.session_state.step = 1
if "video_data" not in st.session_state:
    st.session_state.video_data = None

st.markdown(f"### 🎯 বর্তমান অবস্থান: **ধাপ {st.session_state.step}**")
st.markdown("---")

def save_bytes_to_file(bytes_data, file_path):
    with open(file_path, "wb") as f:
        f.write(bytes_data)

# এফএফএমপ্যাগ প্রসেসিং লাইভ ট্র্যাক করার ফাংশন
def run_ffmpeg_with_progress(cmd, status_text_display):
    progress_bar = st.progress(0)
    total_duration = 1.0
    
    for arg in cmd:
        if "temp_" in arg and os.path.exists(arg):
            try:
                ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
                probe_cmd = [ffmpeg_exe, '-i', arg]
                probe_result = subprocess.run(probe_cmd, stderr=subprocess.PIPE, text=True)
                for line in probe_result.stderr.split('\n'):
                    if 'Duration:' in line:
                        time_str = line.split('Duration:')[1].split(',')[0].strip()
                        h, m, s = time_str.split(':')
                        total_duration = float(h)*3600 + float(m)*60 + float(s)
                        break
            except:
                pass

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    time_regex = re.compile(r'time=(\d+):(\d+):(\d+\.\d+)')
    
    while True:
        line = process.stdout.readline()
        if not line:
            break
        match = time_regex.search(line)
        if match:
            hours, minutes, seconds = match.groups()
            current_time = float(hours)*3600 + float(minutes)*60 + float(seconds)
            percent = min(int((current_time / total_duration) * 100), 100)
            progress_bar.progress(percent / 100.0)
            status_text_display.markdown(f"⏳ প্রসেসিং হচ্ছে: **{percent}%** সম্পন্ন")
            
    process.wait()
    progress_bar.progress(1.0)
    progress_bar.empty()

# ==========================================
# 🟢  ধাপ ১: ভিডিও আপলোড ও কপিরাইট রিমুভ
# ==========================================
if st.session_state.step == 1:
    st.header("Step ১: ভিডিও আপলোড ও কপিরাইট ফিল্টার")
    uploaded_video = st.file_uploader("আপনার মূল ভিডিও ফাইলটি আপলোড করুন (MP4/MKV)", type=["mp4", "mkv"])
    
    voice_style = st.selectbox("ভয়েজ ও সুর পরিবর্তনের মোড:", [
        "🔥 High Security Voice Changer (পিচ ভারী + ৩% স্পিড চেঞ্জ)",
        "🎵 Creative Lo-Fi Vibe (হালকা ইকো + ২% গতি বৃদ্ধি)",
        "🎙️ Deep Cinematic Echo (রহস্যময় গম্ভীর কণ্ঠ)"
    ])
    
    if uploaded_video is not None:
        if st.button("🚀 ১. কপিরাইট রিমুভ করুন"):
            status_text = st.empty()
            status_text.markdown("🎬 ভিডিও কনভার্ট শুরু হচ্ছে...")
            try:
                ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
                
                for f in [v_start, v_step1, v_step2, v_final]:
                    if os.path.exists(f): os.remove(f)
                    
                with open(v_start, "wb") as f:
                    f.write(uploaded_video.read())
                    
                v_filter = "hflip,crop=in_w*0.94:in_h*0.94:in_w*0.03:in_h*0.03,eq=contrast=1.12:brightness=0.04:saturation=1.15:gamma=0.95,setpts=0.95*PTS"
                
                if "High Security" in voice_style:
                    a_filter = "asetrate=44100*0.93,atempo=1.07,bass=g=5"
                elif "Lo-Fi" in voice_style:
                    a_filter = "atempo=1.03,aecho=0.8:0.85:25:0.2,treble=g=2"
                else:
                    a_filter = "asetrate=44100*0.90,atempo=1.11,aecho=0.8:0.90:35:0.3,bass=g=6"
                    
                cmd = [
                    ffmpeg_exe, '-y', '-i', v_start,
                    '-vf', v_filter, '-af', a_filter,
                    '-r', '24',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22',
                    '-c:a', 'aac', '-b:a', '128k', v_step1
                ]
                
                run_ffmpeg_with_progress(cmd, status_text)
                
                if os.path.exists(v_step1) and os.path.getsize(v_step1) > 0:
                    with open(v_step1, "rb") as f:
                        st.session_state.video_data = f.read()
                    
                    st.session_state.step = 2
                    status_text.success("✅  ধাপ ১ সফল! পরবর্তী ধাপে যাওয়া হচ্ছে...")
                    st.rerun()
                else:
                    st.error("❌ ভিডিও প্রসেস সম্পূর্ণ হয়নি। দয়া করে আবার চেষ্টা করুন।")
                    
            except Exception as e:
                st.error(f"এরর: {str(e)}")
            finally:
                if os.path.exists(v_start): os.remove(v_start)

# ==========================================
# 🟢  ধাপ ২: ভিডিও কাটিং (এবং স্কিপ অপশন)
# ==========================================
elif st.session_state.step == 2:
    st.header("Step ২: ভিডিও কাটিং টাইমলাইন")
    
    if st.session_state.video_data is not None:
        save_bytes_to_file(st.session_state.video_data, v_step1)
        st.video(st.session_state.video_data)
        
        ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
        probe_cmd = [ffmpeg_exe, '-i', v_step1]
        probe_result = subprocess.run(probe_cmd, stderr=subprocess.PIPE, text=True)
        total_seconds = 0.0
        for line in probe_result.stderr.split('\n'):
            if 'Duration:' in line:
                try:
                    time_str = line.split('Duration:')[1].split(',')[0].strip()
                    h, m, s = time_str.split(':')
                    total_seconds = float(h)*3600 + float(m)*60 + float(s)
                    break
                except: pass

        max_mins = int(total_seconds // 60)
        max_secs = int(total_seconds % 60)
        
        st.markdown(f"🎒 **আপনার ভিডিওর মোট সময়:** `{max_mins}` মিনিট `{max_secs}` সেকেন্ড।")
        
        col1, col2 = st.columns(2)
        with col1:
            start_m = st.number_input("শрующих মিনিট (Min):", min_value=0, max_value=max_mins, value=0)
            start_s = st.number_input("শুরুর সেকেন্ড (Sec):", min_value=0, max_value=59, value=0)
        with col2:
            end_m = st.number_input("শেষের মিনিট (Min):", min_value=0, max_value=max_mins, value=max_mins)
            end_s = st.number_input("শেষের সেকেন্ড (Sec):", min_value=0, max_value=59, value=max_secs)

        b_col1, b_col2 = st.columns(2)
        
        with b_col1:
            if st.button("✂️ ২. ভিডিও কাটুন"):
                final_start_seconds = (start_m * 60) + start_s
                final_end_seconds = (end_m * 60) + end_s
                status_text = st.empty()
                status_text.markdown("✂️ ভিডিও ট্রিম বা কাটা শুরু হচ্ছে...")
                
                cut_duration = final_end_seconds - final_start_seconds
                def convert_to_hhmmss(sec_val):
                    h = int(sec_val // 3600)
                    m = int((sec_val % 3600) // 60)
                    s = int(sec_val % 60)
                    return f"{h:02d}:{m:02d}:{s:02d}"
                
                cmd = [
                    ffmpeg_exe, '-y', '-ss', convert_to_hhmmss(final_start_seconds), '-i', v_step1,
                    '-t', convert_to_hhmmss(cut_duration), '-c:v', 'libx264', '-c:a', 'aac', v_step2
                ]
                
                run_ffmpeg_with_progress(cmd, status_text)
                
                if os.path.exists(v_step2) and os.path.getsize(v_step2) > 0:
                    with open(v_step2, "rb") as f: 
                        st.session_state.video_data = f.read()
                    st.session_state.step = 3
                    st.rerun()
                if os.path.exists(v_step1): os.remove(v_step1)
                
        with b_col2:
            if st.button("⏩ কাটিং ছাড়া সরাসরি পরের ধাপে যান"):
                if os.path.exists(v_step1):
                    if os.path.exists(v_step2): os.remove(v_step2)
                    os.rename(v_step1, v_step2)
                    
                    with open(v_step2, "rb") as f:
                        st.session_state.video_data = f.read()
                    st.session_state.step = 3
                    st.rerun()

# ==========================================
# 🟢  ধাপ ৩: কাস্টম থাম্বনেইল ও ফাইনাল ডাউনলোড
# ==========================================
elif st.session_state.step == 3:
    st.header("Step ৩: কাস্টম থাম্বনেইল ও ফাইনাল ডাউনলোড")
    uploaded_image = st.file_uploader("📷 থাম্বনেইল ছবি আপলোড করুন (না দিলেও নিচের স্কিপ বোতাম চাপুন):", type=["jpg", "jpeg", "png"])
    
    t_col1, t_col2 = st.columns(2)
    
    with t_col1:
        if st.button("🎬 কাস্টম থাম্বনেইলসহ রেন্ডার করুন"):
            if uploaded_image is not None and st.session_state.video_data is not None:
                save_bytes_to_file(st.session_state.video_data, v_step2)
                ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
                
                with open("temp_thumb.jpg", "wb") as f: 
                    f.write(uploaded_image.read())
                    
                status_text = st.empty()
                status_text.markdown("🎨 ২ সেকেন্ডের থাম্বনেইল সেট এবং অডিও মেলানো হচ্ছে...")
                
                # 🎯 ফিক্স: থাম্বনেইল ঠিক ২ সেকেন্ড থাকবে (lte(t,2)) এবং অডিও নিখুঁত ২ সেকেন্ড ডিলে হবে (adelay=2000)
                cmd = [
                    ffmpeg_exe, '-y', '-i', v_step2, '-i', "temp_thumb.jpg",
                    '-filter_complex', 
                    '[1:v]scale=iw:ih[t];[0:v][t]overlay=enable=\'lte(t,2)\':shortest=0[v];'
                    '[0:a]adelay=2000|2000[a]',
                    '-map', '[v]', '-map', '[a]',
                    '-c:v', 'libx264', '-crf', '20', '-c:a', 'aac', v_final
                ]
                run_ffmpeg_with_progress(cmd, status_text)
                
                if os.path.exists("temp_thumb.jpg"): os.remove("temp_thumb.jpg")
                
                if os.path.exists(v_final) and os.path.getsize(v_final) > 0:
                    st.success("🎉 আলহামদুলিল্লাহ সুজন ভাই! কাস্টম থাম্বনেইলসহ ভিডিও রেডি।")
                    with open(v_final, "rb") as video_file: st.video(video_file.read())
                    with open(v_final, "rb") as file:
                        st.download_button(label="⬇️ গ্যালারিতে সেভ করুন", data=file, file_name="sujon_copyright_pro.mp4", mime="video/mp4")
            else:
                st.error("❌ ভাই, আগে একটি থাম্বনেইল ছবি আপলোড করুন অথবা পাশের স্কিপ বোতামটি ব্যবহার করুন।")

    with t_col2:
        # 🎯 সুজন ভাইয়ের স্পেশাল বোতাম ২: থাম্বনেইল ছাড়া সরাসরি ভিডিও সেভ করা
        if st.button("⏩ থাম্বনেইল ছাড়া ফাইনাল ভিডিও ডাউনলোড করুন"):
            if st.session_state.video_data is not None:
                save_bytes_to_file(st.session_state.video_data, v_step2)
                if os.path.exists(v_final): os.remove(v_final)
                os.rename(v_step2, v_final)
                
                st.success("🎉 আলহামদুলিল্লাহ সুজন ভাই! থাম্বনেইল ছাড়া অরিজিনাল অডিও সিঙ্কেই ভিডিও রেডি।")
                with open(v_final, "rb") as video_file: st.video(video_file.read())
                with open(v_final, "rb") as file:
                    st.download_button(label="⬇️ গ্যালারিতে সেভ করুন", data=file, file_name="sujon_copyright_pro.mp4", mime="video/mp4")

    st.markdown("---")
    if st.button("🔄 নতুন ভিডিও এডিটিং শুরু করুন"):
        for f in [v_start, v_step1, v_step2, v_final]:
            if os.path.exists(f): os.remove(f)
        st.session_state.step = 1
        st.session_state.video_data = None
        st.rerun()
