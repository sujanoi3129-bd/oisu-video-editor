import streamlit as st
import subprocess
import os
import imageio_ffmpeg as im_ffmpeg
from PIL import Image, ImageDraw, ImageFont

# বড় ফাইল আপলোডের জন্য সাইজ লিমিট ২০০০ MB
st._config.set_option("server.maxUploadSize", 2000)

st.set_page_config(page_title="Smart Video Editor Pro", page_icon="🎬", layout="centered")

st.title("🎬 Anti-Copyright Engine (Final Text Fix)")
st.write("ভাই, পেজের নাম যেন মিস না হয়, তার জন্য পিক্সেল ফরম্যাট ফিক্স করা হয়েছে!")

# অস্থায়ী ফাইলের নামসমূহ
v_step2 = "temp_2_cropped.mp4"
v_step3 = "temp_3_named.mp4"
v_final = "final_perfect_video.mp4"
watermark_path = "watermark_text.png"

if "step" not in st.session_state: st.session_state.step = 1
if "video_data" not in st.session_state: st.session_state.video_data = None

# ==========================================
# 🟢 ধাপ ৩: পেজের নাম (ওয়াটারমার্ক) বসানো - ফিক্সড কোড
# ==========================================
if st.session_state.step == 3:
    st.header("Step ৩: আপনার পেজের নাম (Branding Fix)")
    page_name = st.text_input("পেজের নাম লিখুন:", placeholder="ToonFlix")
    
    if st.button("✍️ ৩. পেজের নাম যুক্ত করুন"):
        if page_name:
            with st.spinner("ভিডিওর ওপরে নাম খোদাই করা হচ্ছে..."):
                try:
                    ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
                    # মেমোরি থেকে ভিডিও ডিস্কে রাইট
                    with open(v_step2, "wb") as f: f.write(st.session_state.video_data)
                    
                    # নাম যুক্ত করার শক্তিশালী কম্যান্ড (format=yuv420p জোর করে বসানো)
                    cmd = [
                        ffmpeg_exe, '-y', '-i', v_step2,
                        '-vf', f"drawtext=text='{page_name}':fontcolor=white@0.8:fontsize=50:x=(w-text_w)/2:y=(h-text_h)*0.9:box=1:boxcolor=black@0.5:boxborderw=5,format=yuv420p",
                        '-c:v', 'libx264', '-crf', '20', '-c:a', 'copy', v_step3
                    ]
                    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                    if os.path.exists(v_step3):
                        with open(v_step3, "rb") as f: st.session_state.video_data = f.read()
                        st.success("✅ পেজের নাম এবার বসেই গেছে ভাই!")
                        st.session_state.step = 4
                        st.rerun()
                except Exception as e:
                    st.error(f"এরর: {str(e)}")
        else:
            st.warning("নামটা তো লিখুন ভাই!")

# --- বাকি ধাপগুলো (১, ২, ৪) আগের মতো অপরিবর্তিত থাকবে ---
# নোট: শুধু ধাপ ৩-এর এই অংশটুকু আপনার আগের কোডে প্রতিস্থাপন করলেই হবে।
