import streamlit as st
import subprocess
import os
import re
import imageio_ffmpeg as im_ffmpeg
from PIL import Image, ImageDraw, ImageFont

# বড় ফাইল আপলোডের জন্য সাইজ লিমিট ২০০০ MB করা হলো
st._config.set_option("server.maxUploadSize", 2000)

st.set_page_config(page_title="Smart Video Editor Pro", page_icon="🎬", layout="centered")

st.title("🎬 Anti-Copyright Master Video Engine (With Live % Progress)")
st.write("সুজন ভাই, এখন প্রতিটি ধাপে ভিডিও প্রসেসিং ঠিক কত পার্সেন্ট (`%`) হচ্ছে তা লাইভ দেখতে পাবেন!")

# अस्थायी ফাইল ট্র্যাকিং পাথসমূহ
v_start = "temp_0_input.mp4"
v_step1 = "temp_1_copyright_free.mp4"
v_step2 = "temp_2_cropped.mp4"
v_step3 = "temp_3_named.mp4"
v_final = "final_perfect_video.mp4"
watermark_path = "temp_watermark_text.png"
preview_img_path = "temp_preview_frame.jpg"

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

# 🎯 এফএফএমপ্যাগ প্রসেসিং লাইভ ট্র্যাক করার ম্যাজিক ফাংশন
def run_ffmpeg_with_progress(cmd, status_text_display):
    progress_bar = st.progress(0)
    # ভিডিওর মোট ডিউরেশন সেকেন্ডে বের করার চেষ্টা
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

    # এফএফএমপ্যাগ সাবপ্রসেস চালু
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    
    time_regex = re.compile(r'time=(\d+):(\d+):(\d+\.\d+)')
    
    while True:
        line = process.stdout.readline()
        if not line:
            break
        
        # টাইম আউটপুট স্ক্যান করা হচ্ছে
        match = time_regex.search(line)
        if match:
            hours, minutes, seconds = match.groups()
            current_time = float(hours)*3600 + float(minutes)*60 + float(seconds)
            
            # পার্সেন্টেজ হিসাব
            percent = min(int((current_time / total_duration) * 100), 100)
            progress_bar.progress(percent / 100.0)
            status_text_display.markdown(f"⏳ প্রসেসিং হচ্ছে: **{percent}%** সম্পন্ন")
            
    process.wait()
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
                with open(v_start, "wb") as f:
                    f.write(uploaded_video.read())
                    
                v_filter = "crop=in_w*0.97:in_h*0.97:in_w*0.015:in_h*0.015,eq=contrast=1.07:brightness=0.02:saturation=1.05"
                
                if "High Security" in voice_style:
                    a_filter = "asetrate=44100*0.93,atempo=1.07,bass=g=5"
                elif "Lo-Fi" in voice_style:
                    a_filter = "atempo=1.03,aecho=0.8:0.85:25:0.2,treble=g=2"
                else:
                    a_filter = "asetrate=44100*0.90,atempo=1.11,aecho=0.8:0.90:35:0.3,bass=g=6"
                    
                cmd = [
                    ffmpeg_exe, '-y', '-i', v_start,
                    '-vf', v_filter, '-af', a_filter,
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22',
                    '-c:a', 'aac', '-b:a', '192k', v_step1
                ]
                
                # লাইভ পার্সেন্টেজ রানার
                run_ffmpeg_with_progress(cmd, status_text)
                
                if os.path.exists(v_step1) and os.path.getsize(v_step1) > 0:
                    with open(v_step1, "rb") as f:
                        st.session_state.video_data = f.read()
                    st.success("✅  ধাপ ১ সফল! কপিরাইট মুক্ত করা সম্পন্ন হয়েছে।")
                    st.session_state.step = 2
                    st.rerun()
            except Exception as e:
                st.error(f"এরর: {str(e)}")
            finally:
                if os.path.exists(v_start): os.remove(v_start)

# ==========================================
# 🟢  ধাপ ২: ভিডিও দেখে মিনিট-সেকেন্ডে কাটা
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
            start_m = st.number_input("শুরুর মিনিট (Min):", min_value=0, max_value=max_mins, value=0)
            start_s = st.number_input("শুরুর সেকেন্ড (Sec):", min_value=0, max_value=59, value=0)
        with col2:
            end_m = st.number_input("শেষের মিনিট (Min):", min_value=0, max_value=max_mins, value=max_mins)
            end_s = st.number_input("শেষের সেকেন্ড (Sec):", min_value=0, max_value=59, value=max_secs)

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
                with open(v_step2, "rb") as f: st.session_state.video_data = f.read()
                st.success("✅  ধাপ ২ সফল!")
                st.session_state.step = 3
                st.rerun()
            if os.path.exists(v_step1): os.remove(v_step1)

# ==========================================
# 🟢  ধাপ ৩: হাই-কোয়ালিটি ব্র্যান্ডিং ও সাইজ ফিক্স
# ==========================================
elif st.session_state.step == 3:
    st.header("Step ৩: লাইভ প্রিভিউ দেখে সাইজ ও পজিশন মেলান")
    
    if st.session_state.video_data is not None:
        save_bytes_to_file(st.session_state.video_data, v_step2)
        ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
        
        if not os.path.exists(preview_img_path):
            extract_cmd = [ffmpeg_exe, '-y', '-i', v_step2, '-ss', '00:00:01', '-vframes', '1', preview_img_path]
            subprocess.run(extract_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
        v_w, v_h = 1280, 720
        probe_cmd = [ffmpeg_exe, '-i', v_step2]
        probe_result = subprocess.run(probe_cmd, stderr=subprocess.PIPE, text=True)
        for line in probe_result.stderr.split('\n'):
            if 'Video:' in line and ',' in line:
                parts = line.split(',')
                for part in parts:
                    if 'x' in part:
                        try:
                            dims = part.strip().split(' ')[0].split('x')
                            if len(dims) >= 2 and dims[0].isdigit():
                                v_w, v_h = int(dims[0]), int(dims[1])
                                break
                        except: pass

        page_name = st.text_input("আপনার পেজের নাম এখানে লিখুন:", value="ToonFlix")
        
        st.markdown("### 🎛️ টেক্সট কন্ট্রোল প্যানেল:")
        font_scale = st.slider("📐 লেখার সাইজ বড়/ছোট করুন (Font Size Multiplier):", min_value=1.0, max_value=6.0, value=2.5, step=0.1)
        pos_x = st.slider("⬅️ ডানে-বামে সরান (X Position):", min_value=0, max_value=v_w, value=int(v_w * 0.80))
        pos_y = st.slider("⬇️ ওপরে-নিচে সরান (Y Position):", min_value=0, max_value=v_h, value=40)
        
        if os.path.exists(preview_img_path) and page_name:
            base_image = Image.open(preview_img_path).convert("RGBA")
            base_image = base_image.resize((v_w, v_h))
            
            char_w = 6
            char_h = 11
            temp_tw = char_w * len(page_name)
            temp_th = char_h
            
            text_canvas = Image.new('RGBA', (temp_tw + 4, temp_th + 4), (0, 0, 0, 0))
            text_draw = ImageDraw.Draw(text_canvas)
            
            for dx in [0, 1, 2]:
                for dy in [0, 1]:
                    text_draw.text((dx, dy), page_name, fill=(255, 255, 255, 255))
            
            final_tw = int(temp_tw * font_scale)
            final_th = int(temp_th * font_scale)
            scaled_text = text_canvas.resize((final_tw, final_th), Image.Resampling.NEAREST)
            
            watermark_img = Image.new('RGBA', (v_w, v_h), (0, 0, 0, 0))
            w_draw = ImageDraw.Draw(watermark_img)
            
            padding_x = int(12 * (font_scale * 0.5))
            padding_y = int(8 * (font_scale * 0.5))
            bx1 = pos_x - padding_x
            by1 = pos_y - padding_y
            bx2 = pos_x + final_tw + padding_x
            by2 = pos_y + final_th + padding_y
            
            w_draw.rounded_rectangle([bx1, by1, bx2, by2], radius=6, fill=(0, 0, 0, 160))
            watermark_img.alpha_composite(scaled_text, dest=(pos_x, pos_y))
            
            st.markdown("#### 📺 লাইভ স্ক্রিন প্রিভিউ:")
            base_image.alpha_composite(watermark_img)
            st.image(base_image, use_container_width=True)
            
        if st.button("🎬 ৪. এই মাপে পেজের নাম লক করুন"):
            status_text = st.empty()
            status_text.markdown("🏷️ পুরো ভিডিওতে নাম যুক্ত করা হচ্ছে...")
            try:
                watermark_img.save(watermark_path)
                
                cmd = [
                    ffmpeg_exe, '-y', '-i', v_step2, '-i', watermark_path,
                    '-filter_complex', '[0:v][1:v]overlay=0:0:shortest=0,format=yuv420p[v]',
                    '-map', '[v]', '-map', '0:a',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22', '-c:a', 'copy', v_step3
                ]
                
                run_ffmpeg_with_progress(cmd, status_text)
                
                if os.path.exists(v_step3) and os.path.getsize(v_step3) > 0:
                    with open(v_step3, "rb") as f: st.session_state.video_data = f.read()
                    st.success("✅ নাম সফলভাবে ভিডিওতে বসে গেছে!")
                    st.session_state.step = 4
                    st.rerun()
            except Exception as e:
                st.error(f"ভুল হয়েছে: {str(e)}")
            finally:
                if os.path.exists(v_step2): os.remove(v_step2)
                if os.path.exists(watermark_path): os.remove(watermark_path)
                if os.path.exists(preview_img_path): os.remove(preview_img_path)

# ==========================================
# 🟢   ধাপ ৪: থাম্বনেইল সেট এবং ফাইনাল ডাউনলোড
# ==========================================
elif st.session_state.step == 4:
    st.header("Step ৪: কাস্টম থাম্বনেইল ও ফাইনাল ডাউনলোড")
    uploaded_image = st.file_uploader("📷 থাম্বনেইল ছবি আপলোড করুন (না দিলেও সমস্যা নেই):", type=["jpg", "jpeg", "png"])
    
    if st.button("🎬 ফাইনাল ভিডিও রেন্ডার করুন"):
        if st.session_state.video_data is not None:
            save_bytes_to_file(st.session_state.video_data, v_step3)
            ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
            
            if uploaded_image is not None:
                with open("temp_thumb.jpg", "wb") as f: f.write(uploaded_image.read())
                status_text = st.empty()
                status_text.markdown("🎨 থাম্বনেইল এবং অ디오 ফাইনাল সিঙ্ক হচ্ছে...")
                
                cmd = [
                    ffmpeg_exe, '-y', '-i', v_step3, '-i', "temp_thumb.jpg",
                    '-filter_complex', 
                    '[1:v]scale=iw:ih[t];[0:v][t]overlay=enable=\'lte(t,5)\':shortest=0[v];'
                    '[0:a]adelay=5000|5000[a]',
                    '-map', '[v]', '-map', '[a]',
                    '-c:v', 'libx264', '-crf', '20', '-c:a', 'aac', v_final
                ]
                run_ffmpeg_with_progress(cmd, status_text)
                
                if os.path.exists("temp_thumb.jpg"): os.remove("temp_thumb.jpg")
            else:
                os.rename(v_step3, v_final)
                
            if os.path.exists(v_final) and os.path.getsize(v_final) > 0:
                st.success("🎉 আলহামদুলিল্লাহ সুজন ভাই! আপনার এডিটিং প্রসেস সফল হয়েছে।")
                with open(v_final, "rb") as video_file: st.video(video_file.read())
                with open(v_final, "rb") as file:
                    st.download_button(
                        label="⬇️ গ্যালারিতে সেভ করুন (Download Perfect Video)",
                        data=file,
                        file_name="sujon_anti_copyright_pro.mp4",
                        mime="video/mp4"
                    )
            else:
                st.error("❌ ফাইনাল রেন্ডারিং এ সমস্যা হয়েছে।")

    st.markdown("---")
    if st.button("🔄 নতুন ভিডিও এডিটিং শুরু করুন"):
        for f in [v_start, v_step1, v_step2, v_step3, v_final, preview_img_path]:
            if os.path.exists(f): os.remove(f)
        st.session_state.step = 1
        st.session_state.video_data = None
        st.rerun()
