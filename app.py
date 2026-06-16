import streamlit as st
import subprocess
import os
import imageio_ffmpeg as im_ffmpeg
import struct

# বড় ফাইল আপলোডের জন্য সাইজ লিমিট ২০০০ MB বা ২ GB করা হলো (সবার উপরে থাকতে হবে)
st._config.set_option("server.maxUploadSize", 2000)

st.set_page_config(page_title="Video Copyright Remover", page_icon="🎬", layout="centered")

st.title("🎬 Smart Video Copyright Remover")
st.write("ভিডিও আপলোড করুন। আপনার ভিডিও যতটুকু লম্বা, কাটিং সিস্টেম ঠিক ততটুকুই দেখাবে।")

# এখন এখানে ২০০ MB এর পরিবর্তে ২০00 MB বা ২ GB পর্যন্ত বড় ভিডিও আপলোড করতে পারবেন
uploaded_file = st.file_uploader("১. গ্যালারি থেকে মূল ভিডিও সিলেক্ট করুন (সর্বোচ্চ ২ GB)", type=["mp4"])

# এমপি৪ ফাইলের হেডার থেকে দৈর্ঘ্য বের করার লজিক
def get_mp4_duration(file_stream):
    try:
        file_stream.seek(0)
        data = file_stream.read(10000)
        file_stream.seek(0)
        
        mvhd_idx = data.find(b'mvhd')
        if mvhd_idx != -1:
            version = data[mvhd_idx + 4]
            if version == 0:
                timescale, duration = struct.unpack('>II', data[mvhd_idx + 16:mvhd_idx + 24])
            else:
                timescale, duration = struct.unpack('>QQ', data[mvhd_idx + 20:mvhd_idx + 36])
            
            if timescale > 0:
                return round(duration / timescale, 2)
    except:
        pass
    return 10.50

if uploaded_file is not None:
    input_path = "temp_input.mp4"
    output_path = "my_branded_video.mp4"
    
    video_duration = get_mp4_duration(uploaded_file)
    
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())
        
    st.success("✅ মূল ভিডিও আপলোড সফল হয়েছে!")
    st.markdown("---")
    
    st.markdown("### 📺 ভিডিও প্রিভিউ:")
    with open(input_path, "rb") as video_file:
        video_bytes = video_file.read()
    st.video(video_bytes)

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
            with st.spinner("ভিডিও প্রসেস, কাটিং ও কপিরাইট রিমুভ করার কাজ চলছে..."):
                try:
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    
                    ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
                    
                    # ক্রপ ফিল্টার বাড়িয়ে ৪০ পিক্সেল করা হয়েছে এবং কালার সামান্য পরিবর্তন করা হয়েছে
                    vf_filter = "crop=iw-40:ih-40:20:20,eq=brightness=0.04:contrast=1.04:saturation=1.05"
                    
                    # অডিওর ফিল্টার পরিবর্তন করে স্পিড ও টোন আরেকটু বাড়ানো হলো যাতে কপিরাইট ফ্রি হয়
                    af_filter = "asetrate=44100*1.05,atempo=1.02"
                    
                    command = [
                        ffmpeg_exe, '-y',
                        '-i', input_path,
                        '-ss', f"{total_start_seconds:.2f}",
                        '-to', f"{total_end_seconds:.2f}",
                        '-vf', vf_filter,
                        '-af', af_filter,
                        '-c:v', 'libx264',
                        '-preset', 'veryfast',
                        '-crf', '22',
                        '-c:a', 'aac',
                        output_path
                    ]
                    
                    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                        st.success("🎉 আলহামদুলিল্লাহ! আপনার ভিডিওটি সফলভাবে তৈরি হয়েছে।")
                        
                        with open(output_path, "rb") as file:
                            st.download_button(
                                label="⬇️ গ্যালারিতে সেভ করুন (Download Video)",
                                data=file,
                                file_name="cut_copyright_removed.mp4",
                                mime="video/mp4"
                            )
                    else:
                        st.error("❌ প্রসেসিং সম্পূর্ণ করা যায়নি। নিচে এরর ডিটেইলস দেওয়া হলো:")
                        st.code(result.stderr)
                    
                    if os.path.exists(input_path): os.remove(input_path)
                    
                except Exception as e:
                    st.error(f"দুঃখিত, একটি ইন্টারনাল এরর হয়েছে: {str(e)}")
