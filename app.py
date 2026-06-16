import streamlit as st
import subprocess
import os
import imageio_ffmpeg as im_ffmpeg
from PIL import Image, ImageDraw, ImageFont

# বড় ফাইল আপলোডের জন্য সাইজ লিমিট ২০০০ MB
st._config.set_option("server.maxUploadSize", 2000)

st.set_page_config(page_title="Smart Video Editor", page_icon="🎬", layout="centered")

st.title("🎬 Step-by-Step Anti-Copyright Video Engine")
st.write("সুজন ভাইয়ের দেওয়া বুদ্ধিতে একের পর এক ধাপে নিখুঁত এডিটিং সিস্টেম ভাই!")

# ফাইল পাথের ট্র্যাকিং (যাতে এক ধাপের আউটপুট পরের ধাপে যায়)
v_start = "temp_0_input.mp4"
v_step1 = "temp_1_copyright_free.mp4"
v_step2 = "temp_2_cropped.mp4"
v_step3 = "temp_3_named.mp4"
v_final = "final_perfect_video.mp4"
watermark_path = "temp_watermark_text.png"

# সেশন স্টেট ইনিশিয়েলাইজেশন (ধাপগুলো মনে রাখার জন্য)
if "step" not in st.session_state:
    st.session_state.step = 1

st.markdown("---")

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
            with st.spinner("ভিডিও জুম, কালার গ্রাফিক্স এবং অডিও ফিল্টার করা হচ্ছে..."):
                try:
                    ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
                    with open(v_start, "wb") as f:
                        f.write(uploaded_video.read())
                        
                    # কপিরাইট ফিল্টার (ভিডিও সোজা রেখে ৩% ক্রপ ও কালার মিক্স)
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
                        st.success("✅ ধাপ ১ সফল! কপিরাইট মুক্ত করা সম্পন্ন হয়েছে।")
                        st.session_state.step = 2
                        st.rerun()
                    else:
                        st.error("❌ ফিল্টারে সমস্যা হয়েছে ভাই। কোড চেক করুন।")
                except Exception as e:
                    st.error(f"এরর: {str(e)}")

# ==========================================
# 🟢 ধাপ ২: ভিডিওর অপ্রয়োজনীয় অংশ কাটা
# ==========================================
elif st.session_state.step == 2:
    st.header("Step ২: ভিডিও কাটিং টাইমলাইন")
    st.write("কপিরাইট মুক্ত ভিডিওটি সচল হয়েছে। এবার অপ্রয়োজনীয় অংশ কেটে বাদ দিন ভাই।")
    
    ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
    
    # ভিডিওর মোট ডিউরেশন বের করা
    probe_cmd = [ffmpeg_exe, '-i', v_step1]
    probe_result = subprocess.run(probe_cmd, stderr=subprocess.PIPE, text=True)
    duration = 10.0 # ডিফল্ট
    for line in probe_result.stderr.split('\n'):
        if 'Duration:' in line:
            try:
                time_str = line.split('Duration:')[1].split(',')[0].strip()
                h, m, s = time_str.split(':')
                duration = float(h)*3600 + float(m)*60 + float(s)
                break
            except:
                pass

    start_time = st.number_input("কাটার শুরুর সময় (সেকেন্ড):", min_value=0.0, max_value=duration, value=0.0)
    end_time = st.number_input("কাটার শেষের সময় (সেকেন্ড):", min_value=0.1, max_value=duration, value=duration)
    
    if st.button("✂️ ২. ভিডিও কাটুন"):
        with st.spinner("ভিডিওর নির্দিষ্ট অংশ নিখুঁতভাবে কাটা হচ্ছে..."):
            cut_duration = end_time - start_time
            cmd = [
                ffmpeg_exe, '-y', '-ss', str(start_time), '-i', v_step1,
                '-t', str(cut_duration), '-c', 'copy', v_step2
            ]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            if os.path.exists(v_step2) and os.path.getsize(v_step2) > 0:
                st.success("✅ ধাপ ২ সফল! ভিডিও সফলভাবে কাটা হয়েছে।")
                st.session_state.step = 3
                st.rerun()
            else:
                st.error("❌ ভিডিও কাটতে সমস্যা হয়েছে ভাই।")

# ==========================================
# 🟢 🎬 ধাপ ৩: পেজের নাম (Watermark) বসানো
# ==========================================
elif st.session_state.step == 3:
    st.header("Step ৩: আপনার পেজের নাম (Branding)")
    page_name = st.text_input("আপনার ফেসবুক পেজ বা চ্যানেলের নাম লিখুন:", placeholder="ToonFlix")
    
    if st.button("✍️ ৩. পেজের নাম যুক্ত করুন"):
        if page_name:
            with st.spinner("ভিডিওর ফ্রেম নষ্ট না করে নাম ওপরে বসানো হচ্ছে..."):
                try:
                    ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
                    
                    # ভিডিওর সাইজ চেক করা
                    probe_cmd = [ffmpeg_exe, '-i', v_step2]
                    probe_result = subprocess.run(probe_cmd, stderr=subprocess.PIPE, text=True)
                    v_w, v_h = 1280, 720
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

                    # এক্সাক্ট সাইজের ওয়াটারমার্ক পিকচার তৈরি
                    w_img = Image.new('RGBA', (v_w, v_h), (255, 255, 255, 0))
                    draw = ImageDraw.Draw(w_img)
                    f_size = max(16, int(v_w * 0.035))
                    try:
                        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", f_size)
                    except:
                        font = ImageFont.load_default()
                        
                    tx, ty = int(v_w / 2), int(v_h * 0.90)
                    for off in [(-2,-2), (2,-2), (-2,2), (2,2)]:
                        draw.text((tx+off[0], ty+off[1]), page_name, fill="black", font=font, anchor="mm")
                    draw.text((tx, ty), page_name, fill=(255, 255, 255, 190), font=font, anchor="mm")
                    w_img.save(watermark_path)
                    
                    cmd = [
                        ffmpeg_exe, '-y', '-i', v_step2, '-i', watermark_path,
                        '-filter_complex', '[0:v][1:v]overlay=0:0:shortest=0[v]',
                        '-map', '[v]', '-map', '0:a',
                        '-c:v', 'libx264', '-crf', '22', '-c:a', 'copy', v_step3
                    ]
                    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                    if os.path.exists(v_step3) and os.path.getsize(v_step3) > 0:
                        st.success("✅ ধাপ ৩ সফল! পেজের নাম সুন্দরভাবে স্ক্রিনে বসে গেছে।")
                        st.session_state.step = 4
                        st.rerun()
                except Exception as e:
                    st.error(f"ভুল হয়েছে: {str(e)}")
        else:
            st.warning("ভাই পেজের নামটা তো লিখুন!")

# ==========================================
# 🟢 📷 ধাপ ৪: থাম্বনেইল সেট এবং ফাইনাল ডাউনলোড
# ==========================================
elif st.session_state.step == 4:
    st.header("Step ৪: কাস্টম থাম্বনেইল ও ফাইনাল রেন্ডারিং")
    uploaded_image = st.file_uploader("📷 থাম্বনেইল ছবি আপলোড করুন (Optional):", type=["jpg", "jpeg", "png"])
    
    if st.button("🎬 ৪. ফাইনাল ভিডিও তৈরি ও সেভ করুন"):
        ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
        
        if uploaded_image is not None:
            with open("temp_thumb.jpg", "wb") as f:
                f.write(uploaded_image.read())
                
            with st.spinner("ভিডিওর শুরুতে থাম্বনেইল ইমেজ ফিক্সড করা হচ্ছে..."):
                # থাম্বনেইল ভিডিওর শুরুতে ৫ সেকেন্ড ওপরে দেখাবে
                cmd = [
                    ffmpeg_exe, '-y', '-i', v_step3, '-i', "temp_thumb.jpg",
                    '-filter_complex', '[1:v]scale=iw:ih[t];[0:v][t]overlay=enable=\'lte(t,5)\':shortest=0[v]',
                    '-map', '[v]', '-map', '0:a',
                    '-c:v', 'libx264', '-crf', '22', '-c:a', 'copy', v_final
                ]
                subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            # যদি থাম্বনেইল না দেয়, ধাপ ৩ এর ভিডিওটাই ফাইনাল হবে
            os.rename(v_step3, v_final)
            
        if os.path.exists(v_final) and os.path.getsize(v_final) > 0:
            st.success("🎉 আলহামদুলিল্লাহ সুজন ভাই! ধাপে ধাপে করার কারণে এবার ভিডিওর সাইজ, মোশন, নাম সব নিখুঁত হয়েছে।")
            
            with open(v_final, "rb") as video_file:
                st.video(video_file.read())
                
            with open(v_final, "rb") as file:
                st.download_button(
                    label="⬇️ গ্যালারিতে সেভ করুন (Download Video)",
                    data=file,
                    file_name="master_copyright_free_video.mp4",
                    mime="video/mp4"
                )
                
            # নতুন ফাইল করার জন্য রিসেট বাটন
            if st.button("🔄 নতুন ভিডিও এডিট করুন"):
                for f in [v_start, v_step1, v_step2, v_step3, v_final, watermark_path, "temp_thumb.jpg"]:
                    if os.path.exists(f): os.remove(f)
                st.session_state.step = 1
                st.rerun()
