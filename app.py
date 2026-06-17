import streamlit as st
import subprocess
import os
import imageio_ffmpeg as im_ffmpeg
from PIL import Image, ImageDraw, ImageFont

# বড় ফাইল আপলোডের জন্য সাইজ লিমিট ২০০০ MB
st._config.set_option("server.maxUploadSize", 2000)

st.set_page_config(page_title="Smart Video Editor Pro", page_icon="🎬", layout="centered")

st.title("🎬 Anti-Copyright Master Video Engine")
st.write("সুজন ভাই, এবার আপনার পেজের নাম হবে একদম স্টাইলিশ, মোটা এবং চকচকে 3D Glow এফেক্টে!")

# অস্থায়ী ফাইল ট্র্যাকিং পাথসমূহ
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

# ==========================================
# 🟢 ধাপ ১: ভিডিও আপলোড ও কপিরাইট রিমুভ
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
            with st.spinner("ভিডিও জুম, কালার গ্রাফিক্স এবং অ디오 ফিল্টার করা হচ্ছে..."):
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
                    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
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
# 🟢 ধাপ ২: ভিডিও দেখে মিনিট-সেকেন্ডে কাটা
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
            
            with st.spinner("ভিডিও কাটা হচ্ছে..."):
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
                subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                if os.path.exists(v_step2) and os.path.getsize(v_step2) > 0:
                    with open(v_step2, "rb") as f: st.session_state.video_data = f.read()
                    st.success("✅  ধাপ ২ সফল!")
                    st.session_state.step = 3
                    st.rerun()
                if os.path.exists(v_step1): os.remove(v_step1)

# ==========================================
# 🟢 🎬 🎯 💥 ধাপ ৩: চকচকে প্রফেশনাল টেক্সট (Watermark Fix)
# ==========================================
elif st.session_state.step == 3:
    st.header("Step ৩: আপনার পেজের চকচকে লোগো বসান")
    st.write("সুজন ভাই, এখন নিচের স্লাইডার নাড়ালেই লেখা কোথায় যাচ্ছে তা ছবির ওপরে একদম চকচকে লোগোর মতো লাইভ দেখতে পাবেন।")
    
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

        page_name = st.text_input("আপনার পেজের নাম এখানে লিখুন (যেমন: Toon Flix):", value="Toon Flix")
        
        st.markdown("### 🎛️ এডজাস্টমেন্ট টুলস:")
        font_size = st.slider("📐 লোগোর সাইজ (Font Size):", min_value=15, max_value=150, value=65, step=2)
        pos_x = st.slider("⬅️ ডানে-বামে সরান (X Position):", min_value=0, max_value=v_w, value=int(v_w * 0.72))
        pos_y = st.slider("⬇️ ওপরে-নিচে সরান (Y Position):", min_value=0, max_value=v_h, value=int(v_h * 0.88))
        
        if os.path.exists(preview_img_path) and page_name:
            base_image = Image.open(preview_img_path).convert("RGBA")
            base_image = base_image.resize((v_w, v_h))
            
            # Pillow দিয়ে চকচকে (Glow effect) টেক্সট ইমেজ তৈরির লজিক
            w_img = Image.new('RGBA', (v_w, v_h), (255, 255, 255, 0))
            w_draw = ImageDraw.Draw(w_img)
            font = ImageFont.load_default()
            
            # টেক্সটের দৈর্ঘ্য ও উচ্চতা নির্ণয়
            t_w_calc = int(len(page_name) * (font_size * 0.65))
            t_h_calc = int(font_size * 1.4)
            
            # চকচকে এফেক্টের জন্য লেখাটিকে বড় করে রেন্ডার করার টেকনিক
            text_canvas = Image.new('RGBA', (len(page_name)*25, 30), (0, 0, 0, 0))
            text_draw = ImageDraw.Draw(text_canvas)
            
            # মোটা এবং গ্লো করার জন্য কয়েকবার ওভারল্যাপ করা (Bold & Glow hack)
            for offset in [(0,0), (2,0), (0,2), (2,2), (1,1)]:
                text_draw.text((3 + offset[0], 3 + offset[1]), page_name, fill=(255, 255, 255, 255), font=font)
                
            # লেখাটিকে প্রমাণ সাইজে বড় করা হলো
            scaled_text = text_canvas.resize((t_w_calc, t_h_calc), Image.Resampling.NEAREST)
            
            # ছবির ওপর বসানো
            w_img.alpha_composite(scaled_text, dest=(pos_x, pos_y))
            
            st.markdown("#### 📺 লাইভ লোগো প্রিভিউ (চকচকে এবং পরিষ্কার):")
            # ছবির ওপর ওয়াটারমার্ক বসানো Live Preview
            base_image.alpha_composite(w_img, dest=(0, 0))
            st.image(base_image, use_container_width=True)
            
        if st.button("🎬 ৪. এই মাপে লোগো النهائية লক করে ভিডিও তৈরি করুন"):
            with st.spinner("পুরো ভিডিওতে নাম নিখুঁতভাবে বসানো হচ্ছে..."):
                try:
                    w_img.save(watermark_path)
                    
                    # এফএফএমপ্যাগ দিয়ে ইমেজ ওভারলে ও পিক্সেল ফরম্যাট ফিক্স করা
                    cmd = [
                        ffmpeg_exe, '-y', '-i', v_step2, '-i', watermark_path,
                        '-filter_complex', '[0:v][1:v]overlay=0:0:shortest=0,format=yuv420p[v]',
                        '-map', '[v]', '-map', '0:a',
                        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22', '-c:a', 'copy', v_step3
                    ]
                    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                    if os.path.exists(v_step3) and os.path.getsize(v_step3) > 0:
                        with open(v_step3, "rb") as f: st.session_state.video_data = f.read()
                        st.success("✅ নাম সফলভাবে চকচকে লোগো এফেক্টে ভিডিওতে বসে গেছে!")
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
                with st.spinner("th থাম্বনেইল সেট করা হচ্ছে..."):
                    cmd = [
                        ffmpeg_exe, '-y', '-i', v_step3, '-i', "temp_thumb.jpg",
                        '-filter_complex', '[1:v]scale=iw:ih[t];[0:v][t]overlay=enable=\'lte(t,5)\':shortest=0[v]',
                        '-map', '[v]', '-map', '0:a',
                        '-c:v', 'libx264', '-crf', '20', '-c:a', 'copy', v_final
                    ]
                    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if os.path.exists("temp_thumb.jpg"): os.remove("temp_thumb.jpg")
            else:
                os.rename(v_step3, v_final)
                
            if os.path.exists(v_final) and os.path.getsize(v_final) > 0:
                st.success("🎉 আলহামদুলিল্লাহ সুজন ভাই! সম্পূর্ণ প্রসেস সফল হয়েছে।")
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
