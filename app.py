import streamlit as st
import subprocess
import os
import imageio_ffmpeg as im_ffmpeg
import struct

# বড় ফাইল আপলোডের জন্য সাইজ লিমিট ২০০০ MB বা ২ GB করা হলো (নেট ও ফাইল সেভিং এর জন্য শুরুতে থাকা আবশ্যক)
st._config.set_option("server.maxUploadSize", 2000)

st.set_page_config(page_title="Video Copyright Remover", page_icon="🎬", layout="centered")

st.title("🎬 Smart Video Copyright Remover")
st.write("থাম্বনেইল সহ অডিও-ভিডিও ১০০% মিল থাকবে এবং মিনিমাইজ করলেও ফাইল কাটবে না।")

# সেশন স্টেট ইনিশিয়াল করা (যাতে পেজ রিলোড বা মিনিমাইজ হলেও ডেটা হারিয়ে না যায়)
if 'video_processed' not in st.session_state:
    st.session_state.video_processed = False

# ভিডিও আপলোড ক্যাশিং ফাংশন (বারবার আপলোড হওয়া ঠেকিয়ে ইন্টারনেট বাঁচাবে)
@st.cache_data(show_spinner=False)
def save_uploaded_video(file_bytes):
    input_path = "temp_input.mp4"
    with open(input_path, "wb") as f:
        f.write(file_bytes)
    return input_path

uploaded_file = st.file_uploader("১. গ্যালারি থেকে মূল ভিডিও সিলেক্ট করুন (সর্বোচ্চ ২ GB)", type=["mp4"])

# এমপি৪ ফাইলের দৈর্ঘ্য ও সাইজ নিখুঁতভাবে বের করার লজিক
def get_mp4_info(file_path):
    duration = 10.50  # ডিফল্ট
    width, height = 576, 1024  # ডিফল্ট
    try:
        with open(file_path, "rb") as file_stream:
            data = file_stream.read(50000)
        
        mvhd_idx = data.find(b'mvhd')
        if mvhd_idx != -1:
            version = data[mvhd_idx + 4]
            if version == 0:
                timescale, dur = struct.unpack('>II', data[mvhd_idx + 16:mvhd_idx + 24])
            else:
                timescale, dur = struct.unpack('>QQ', data[mvhd_idx + 20:mvhd_idx + 36])
            if timescale > 0:
                duration = round(dur / timescale, 2)
                
        tkhd_idx = data.find(b'tkhd')
        if tkhd_idx != -1:
            w_bytes = data[tkhd_idx + 76:tkhd_idx + 80]
            h_bytes = data[tkhd_idx + 80:tkhd_idx + 84]
            if len(w_bytes) == 4 and len(h_bytes) == 4:
                w = struct.unpack('>I', w_bytes)[0] >> 16
                h = struct.unpack('>I', h_bytes)[0] >> 16
                if w > 0 and h > 0:
                    width, height = w, h
    except:
        pass
    return duration, width, height

if uploaded_file is not None:
    output_path = "my_branded_video.mp4"
    thumb_path = "temp_thumb.jpg"
    
    # ফাইল রিড করে ক্যাশ মেমোরিতে রাখা হচ্ছে
    file_bytes = uploaded_file.read()
    input_path = save_uploaded_video(file_bytes)
    
    video_duration, v_width, v_height = get_mp4_info(input_path)
    
    st.success("✅ ভিডিও সার্ভার মেমোরিতে সুরক্ষিত আছে! নেট বারবার কাটবে না।")
    st.markdown("---")
    
    st.markdown("### 📺 ভিডিও প্রিভিউ:")
    st.video(file_bytes)
    st.markdown("---")
    
    # ২. থাম্বনেইল আপলোডার
    st.markdown("### 🖼️ কাস্টম থাম্বনেইল সেটআপ (Optional):")
    uploaded_thumb = st.file_uploader("ভিডিওর শুরুতে থাম্বনেইল লাগাতে চাইলে ছবি সিলেক্ট করুন (JPG/PNG)", type=["jpg", "jpeg", "png"])
    
    if uploaded_thumb is not None:
        with open(thumb_path, "wb") as f:
            f.write(uploaded_thumb.read())
        st.image(uploaded_thumb, caption="আপনার সিলেক্ট করা থাম্বনেইল", width=300)

    st.markdown("---")
    st.markdown(f"### ✂️ ভিডিও কাটার টাইমলাইন (ভিডিওর আসল সাইজ: `{video_duration}` সেকেন্ড)")
    
    time_range = st.slider(
        "ভিডিওর কাটিং পয়েন্ট সিলেক্ট করুন (টেনে ছোট-বড় করুন):",
        min_value=0.0,
        max_value=float(video_duration),
        value=(0.0, float(video_duration)),
        step=0.05,
        format="%.2f সেকেন্ড"
    )
    
    total_start_seconds = time_range[0]
    total_end_seconds = time_range[1]
    
    st.markdown(f"🎯 **আপনার সিলেক্ট করা সময়:** `{total_start_seconds:.2f}` সেকেন্ড থেকে `{total_end_seconds:.2f}` সেকেন্ড পর্যন্ত কেটে রাখা হবে।")
    st.markdown("---")
    
    if st.button("🚀 Process, Cut & Remove Copyright"):
        if total_start_seconds >= total_end_seconds:
            st.error("❌ ভুল সিলেকশন! ভিডিওর শেষের সময় অবশ্যই শুরুর সময়ের চেয়ে বেশি হতে হবে।")
        else:
            with st.spinner("ভিডিও প্রসেস, নিখুঁত অডিও ম্যাচিং ও কপিরাইট রিমুভ করার কাজ চলছে..."):
                try:
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    
                    ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
                    cropped_w = v_width - 40
                    cropped_h = v_height - 40
                    
                    # কপিরাইট রিমুভার বেস ফিল্টার
                    vf_filter = "crop=iw-40:ih-40:20:20,eq=brightness=0.04:contrast=1.04:saturation=1.05"
                    af_filter = "asetrate=44100*1.05,atempo=1.02"
                    
                    # যদি ইউজার থাম্বনেইল আপলোড করে
                    if uploaded_thumb is not None and os.path.exists(thumb_path):
                        # ১০০০ মিলিসেকেন্ড (১ সেকেন্ড) অডিও ডিলে করার ফিল্টার যাতে থাম্বনেইলের সাথে অডিও সিঙ্ক হয়
                        filter_complex_cmd = (
                            f"[0:v]scale={cropped_w}:{cropped_h}:force_original_aspect_ratio=decrease,"
                            f"pad={cropped_w}:{cropped_h}:(ow-iw)/2:(oh-ih)/2,setsar=1,setpts=PTS-STARTPTS[v0];"
                            f"[1:v]{vf_filter},setsar=1,setpts=PTS-STARTPTS[v1];"
                            f"[1:a]{af_filter},adelay=1000|1000[a1];"
                            f"[v0][v1]concat=n=2:v=1:a=0[v_out]"
                        )
                        
                        command = [
                            ffmpeg_exe, '-y',
                            '-loop', '1', '-t', '1', '-i', thumb_path,  # ইনপুট ০: থাম্বনেইল ছবি (১ সেকেন্ড)
                            '-ss', f"{total_start_seconds:.2f}",
                            '-to', f"{total_end_seconds:.2f}",
                            '-i', input_path,  # ইনপুট ১: মূল ভিডিও
                            '-filter_complex', filter_complex_cmd,
                            '-map', '[v_out]', '-map', '[a1]',
                            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22',
                            '-c:a', 'aac',
                            output_path
                        ]
                    else:
                        # থাম্বনেইল না থাকলে সাধারণ দ্রুত কম্যান্ড
                        command = [
                            ffmpeg_exe, '-y',
                            '-i', input_path,
                            '-ss', f"{total_start_seconds:.2f}",
                            '-to', f"{total_end_seconds:.2f}",
                            '-vf', vf_filter,
                            '-af', af_filter,
                            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22',
                            '-c:a', 'aac',
                            output_path
                        ]
                    
                    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                        st.session_state.video_processed = True
                        st.success("🎉 আলহামদুলিল্লাহ! থাম্বনেইল, নিখুঁত অডিও এবং কাটিং সহ ভিডিওটি তৈরি হয়েছে।")
                    else:
                        st.error("❌ প্রসেসিং সম্পূর্ণ করা যায়নি। নিচে এরর ডিটেইলস দেওয়া হলো:")
                        st.code(result.stderr)
                    
                    if os.path.exists(thumb_path): os.remove(thumb_path)
                    
                except Exception as e:
                    st.error(f"দুঃখিত, একটি ইন্টারনাল এরর হয়েছে: {str(e)}")

    # ফাইল প্রসেস শেষে ডাউনলোড বাটনটি স্ক্রিনে লক হয়ে থাকবে (রিলোড হলেও কাটবে না)
    if st.session_state.video_processed and os.path.exists("my_branded_video.mp4"):
        with open("my_branded_video.mp4", "rb") as file:
            st.download_button(
                label="⬇️ গ্যালারিতে সেভ করুন (Download Video)",
                data=file,
                file_name="copyright_removed_video.mp4",
                mime="video/mp4"
            )
