import streamlit as st
import subprocess
import os
import imageio_ffmpeg as im_ffmpeg
from PIL import Image, ImageDraw, ImageFont

# বড় ফাইল আপলোডের জন্য সাইজ লিমিট ২০০০ MB করা হলো
st._config.set_option("server.maxUploadSize", 2000)

st.set_page_config(page_title="Smart Video Editor Pro", page_icon="🎬", layout="centered")

st.title("🎬 Step-by-Step Anti-Copyright Video Engine")
st.write("ভিডিও দেখে কাটিং করা এবং পেজের নাম ১০০% গ্যারান্টিসহ ওপরে বসানোর ফাইনাল কোড ভাই!")

# অস্থায়ী ফাইলের নামসমূহ
v_start = "temp_0_input.mp4"
v_step1 = "temp_1_copyright_free.mp4"
v_step2 = "temp_2_cropped.mp4"
v_step3 = "temp_3_named.mp4"
v_final = "final_perfect_video.mp4"
watermark_path = "temp_watermark_text.png"

# সেশন স্টেট ইনিশিয়েলাইজেশন (ধাপ এবং ভিডিওর ডেটা মনে রাখার জন্য)
if "step" not in st.session_state:
    st.session_state.step = 1
if "video_data" not in st.session_state:
    st.session_state.video_data = None

st.markdown("---")

# সাহায্যকারী ফাংশন: মেমোরি থেকে ফাইল ডিস্কে লেখা
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
            with st.spinner("ভিডিও জুম, কালার গ্রাফিক্স এবং অডিও ফিল্টার করা হচ্ছে..."):
                try:
                    ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
                    # ইনপুট ফাইল সেভ
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
                        # তৈরি হওয়া ভিডিওর ডেটা সেশন স্টেটে লক করা হলো
                        with open(v_step1, "rb") as f:
                            st.session_state.video_data = f.read()
                        
                        st.success("✅ ধাপ ১ সফল! কপিরাইট মুক্ত করা সম্পন্ন হয়েছে।")
                        st.session_state.step = 2
                        st.rerun()
                    else:
                        st.error("❌ ফিল্টারে সমস্যা হয়েছে ভাই। কোড চেক করুন।")
                except Exception as e:
                    st.error(f"এরর: {str(e)}")
                finally:
                    if os.path.exists(v_start): os.remove(v_start)
                    if os.path.exists(v_step1): os.remove(v_step1)

# ==========================================
# 🟢 ধাপ ২: ভিডিও দেখে কাটা (Time Cutting)
# ==========================================
elif st.session_state.step == 2:
    st.header("Step ২: ভিডিও কাটিং টাইমলাইন")
    st.write("নিচের ভিডিওটি দেখে টাইম (সেকেন্ড) হিসাব করে অপ্রয়োজনীয় অংশ কেটে ফেলুন ভাই।")
    
    if st.session_state.video_data is not None:
        # আগের ধাপের ভিডিও ডিস্কে রাইট করা হচ্ছে প্রিভিউ এবং কাটার জন্য
        save_bytes_to_file(st.session_state.video_data, v_step1)
        
        # 📺 সুজন ভাই এখানে ভিডিও দেখে টাইম সিলেক্ট করতে পারবেন
        st.subheader("📺 ভিডিও প্রিভিউ (এখান থেকে টাইম দেখে নিন):")
        st.video(st.session_state.video_data)
        
        ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
        
        # ভিডিওর মোট আসল ডিউরেশন বের করা
        probe_cmd = [ffmpeg_exe, '-i', v_step1]
        probe_result = subprocess.run(probe_cmd, stderr=subprocess.PIPE, text=True)
        duration = 30.0 # ডিফল্ট ব্যাকআপ
        for line in probe_result.stderr.split('\n'):
            if 'Duration:' in line:
                try:
                    time_str = line.split('Duration:')[1].split(',')[0].strip()
                    h, m, s = time_str.split(':')
                    duration = float(h)*3600 + float(m)*60 + float(s)
                    break
                except:
                    pass

        st.markdown(f"**💡 আপনার ভিডিওর মোট সাইজ/দৈর্ঘ্য:** `{duration:.2f}` সেকেন্ড।")
        
        start_time = st.number_input("কাটার শুরুর সময় (সেকেন্ডে লিখুন):", min_value=0.0, max_value=duration, value=0.0, step=0.5)
        end_time = st.number_input("কাটার শেষের সময় (সেকেন্ডে লিখুন):", min_value=0.1, max_value=duration, value=duration, step=0.5)
        
        if st.button("✂️ ২. ভিডিও কাটুন"):
            if end_time <= start_time:
                st.error("❌ শেষের সময় অবশ্যই শুরুর সময়ের চেয়ে বেশি হতে হবে ভাই!")
            else:
                with st.spinner("ভিডিওর নির্দিষ্ট অংশ নিখুঁতভাবে কাটা হচ্ছে..."):
                    cut_duration = end_time - start_time
                    cmd = [
                        ffmpeg_exe, '-y', '-ss', str(start_time), '-i', v_step1,
                        '-t', str(cut_duration), '-c:v', 'libx264', '-c:a', 'aac', v_step2
                    ]
                    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                    if os.path.exists(v_step2) and os.path.getsize(v_step2) > 0:
                        with open(v_step2, "rb") as f:
                            st.session_state.video_data = f.read()
                        st.success("✅ ধাপ ২ সফল! ভিডিও সফলভাবে কাটা হয়েছে।")
                        st.session_state.step = 3
                        st.rerun()
                    else:
                        st.error("❌ ভিডিও কাটতে সমস্যা হয়েছে ভাই।")
                    
                    if os.path.exists(v_step1): os.remove(v_step1)
                    if os.path.exists(v_step2): os.remove(v_step2)

# ==========================================
# 🟢 🎬 ✍️ ধাপ ৩: পেজের নাম (Watermark) বসানো
# ==========================================
elif st.session_state.step == 3:
    st.header("Step ৩: আপনার পেজের নাম (Branding)")
    st.write("আপনার ফেসবুক পেজ বা চ্যানেলের নাম লিখুন। এটি ভিডিওর ওপরে সুন্দরভাবে বসে যাবে।")
    
    page_name = st.text_input("এখানে নাম লিখুন:", placeholder="ToonFlix")
    
    if st.button("✍️ ৩. পেজের নাম যুক্ত করুন"):
        if page_name:
            with st.spinner("ভিডিওর ওপরে নাম রি-রাইট করা হচ্ছে..."):
                try:
                    if st.session_state.video_data is not None:
                        save_bytes_to_file(st.session_state.video_data, v_step2)
                        
                        ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
                        
                        # ভিডিওর আসল সাইজ ডাইরেক্ট চেক করা
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

                        # ভিডিওর অরিজিনাল সাইজ অনুযায়ী স্বচ্ছ ইমেজ তৈরি
                        w_img = Image.new('RGBA', (v_w, v_h), (255, 255, 255, 0))
                        draw = ImageDraw.Draw(w_img)
                        f_size = max(20, int(v_w * 0.045)) # ফন্ট সাইজ একটু বড় করা হলো
                        
                        try:
                            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", f_size)
                        except:
                            font = ImageFont.load_default()
                            
                        # মাঝখানে এবং নিচ থেকে ১০% ওপরে পজিশন
                        tx, ty = int(v_w / 2), int(v_h * 0.88)
                        
                        # স্ট্রোক বর্ডার ২ গুণ মোটা করা হলো যাতে লেখা ফুটে ওঠে
                        for off in [(-3,-3), (3,-3), (-3,3), (3,3), (-2,0), (2,0), (0,-2), (0,2)]:
                            draw.text((tx+off[0], ty+off[1]), page_name, fill="black", font=font, anchor="mm")
                        # মূল টেক্সট
                        draw.text((tx, ty), page_name, fill=(255, 255, 255, 220), font=font, anchor="mm")
                        w_img.save(watermark_path)
                        
                        # ওভারলে ফিল্টার দিয়ে নিখুঁত মার্জ করা
                        cmd = [
                            ffmpeg_exe, '-y', '-i', v_step2, '-i', watermark_path,
                            '-filter_complex', '[0:v][1:v]overlay=0:0:shortest=0[v]',
                            '-map', '[v]', '-map', '0:a',
                            '-c:v', 'libx264', '-crf', '20', '-c:a', 'copy', v_step3
                        ]
                        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        
                        if os.path.exists(v_step3) and os.path.getsize(v_step3) > 0:
                            with open(v_step3, "rb") as f:
                                st.session_state.video_data = f.read()
                            st.success("✅ Critical ধাপ ৩ সফল! পেজের নাম সুন্দরভাবে স্ক্রিনে বসে গেছে।")
                            st.session_state.step = 4
                            st.rerun()
                        else:
                            st.error("❌ পেজের নাম ওভারলে করতে সমস্যা হয়েছে ভাই।")
                except Exception as e:
                    st.error(f"ভুল হয়েছে: {str(e)}")
                finally:
                    if os.path.exists(v_step2): os.remove(v_step2)
                    if os.path.exists(v_step3): os.remove(v_step3)
                    if os.path.exists(watermark_path): os.remove(watermark_path)
        else:
            st.warning("ভাই পেজের নামটা তো আগে লিখুন!")

# ==========================================
# 🟢 📷 ধাপ ৪: থাম্বনেইল সেট এবং ফাইনাল ডাউনলোড
# ==========================================
elif st.session_state.step == 4:
    st.header("Step ৪: কাস্টম থাম্বনেইল ও ফাইনাল ডাউনলোড")
    uploaded_image = st.file_uploader("📷 থাম্বনেইল ছবি আপলোড করুন (Optional):", type=["jpg", "jpeg", "png"])
    
    if st.button("🎬 ৪. ফাইনাল ভিডিও তৈরি ও সেভ করুন"):
        if st.session_state.video_data is not None:
            save_bytes_to_file(st.session_state.video_data, v_step3)
            ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
            
            if uploaded_image is not None:
                with open("temp_thumb.jpg", "wb") as f:
                    f.write(uploaded_image.read())
                    
                with st.spinner("ভিডিওর শুরুতে থাম্বনেইল ইমেজ সেট করা হচ্ছে..."):
                    # থাম্বনেইল ভিডিওর শুরুতে ৫ সেকেন্ড ওপরে দেখাবে
                    cmd = [
                        ffmpeg_exe, '-y', '-i', v_step3, '-i', "temp_thumb.jpg",
                        '-filter_complex', '[1:v]scale=iw:ih[t];[0:v][t]overlay=enable=\'lte(t,5)\':shortest=0[v]',
                        '-map', '[v]', '-map', '0:a',
                        '-c:v', 'libx264', '-crf', '20', '-c:a', 'copy', v_final
                    ]
                    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if os.path.exists("temp_thumb.jpg"): os.remove("temp_thumb.jpg")
            else:
                # যদি থাম্বনেইল না দেয়, আগের ধাপের টাই ফাইনাল
                os.rename(v_step3, v_final)
                
            if os.path.exists(v_final) and os.path.getsize(v_final) > 0:
                st.success("🎉 আলহামদুলিল্লাহ সুজন ভাই! আপনার দেওয়া বুদ্ধিতে ধাপে ধাপে করার কারণে এবার ভিডিওর সাইজ, মোশন, কাটিং এবং নাম—সব ১০০% নিখুঁত হয়েছে।")
                
                with open(v_final, "rb") as video_file:
                    st.video(video_file.read())
                    
                with open(v_final, "rb") as file:
                    st.download_button(
                        label="⬇️ গ্যালারিতে সেভ করুন (Download Perfect Video)",
                        data=file,
                        file_name="sujon_final_master_video.mp4",
                        mime="video/mp4"
                    )
                if os.path.exists(v_step3): os.remove(v_step3)
            else:
                st.error("❌ ফাইনাল রেন্ডারিং এ সমস্যা হয়েছে।")

    st.markdown("---")
    if st.button("🔄 নতুন ভিডিও এডিটিং শুরু করুন"):
        for f in [v_start, v_step1, v_step2, v_step3, v_final, watermark_path, "temp_thumb.jpg"]:
            if os.path.exists(f): os.remove(f)
        st.session_state.step = 1
        st.session_state.video_data = None
        st.rerun()
