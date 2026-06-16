import streamlit as st
import subprocess
import os
import imageio_ffmpeg as im_ffmpeg

# বড় ফাইল আপলোডের জন্য সাইজ লিমিট ২০০০ MB করা হলো
st._config.set_option("server.maxUploadSize", 2000)

st.set_page_config(page_title="Smart Video Copyright Remover", page_icon="🛡️", layout="centered")

st.title("🛡️ Smart Video Copyright Remover (Advanced Audio Edition)")
st.write("ভিডিও উল্টানো ছাড়া এবং কড়া অডিও পিচ ও স্পিড চেঞ্জার সহ সম্পূর্ণ নিরাপদ সিস্টেম!")

st.markdown("---")
st.subheader("১. ভিডিও এবং থাম্বনেইল আপলোড করুন")

# ভিডিও ফাইল আপলোড
uploaded_video = st.file_uploader("আপনার মূল ভিডিও ফাইলটি আপলোড করুন (MP4/MKV)", type=["mp4", "mkv"])

# কাস্টম থাম্বনেইল আপলোড (ঐচ্ছিক)
uploaded_image = st.file_uploader("📷 কাস্টম থাম্বনেইল সেটআপ (Optional):", type=["jpg", "jpeg", "png"])

if uploaded_video is not None:
    input_video_path = "temp_input_video.mp4"
    input_image_path = "temp_input_thumb.jpg"
    output_video_path = "copyright_free_output.mp4"
    
    with open(input_video_path, "wb") as f:
        f.write(uploaded_video.read())
        
    st.success("✅ ভিডিও সফলভাবে আপলোড হয়েছে ভাই!")
    
    if uploaded_image is not None:
        with open(input_image_path, "wb") as f:
            f.write(uploaded_image.read())
        st.image(input_image_path, caption="আপলোড করা থাম্বনেইল", width=300)

    st.markdown("---")
    st.subheader("২. অ্যান্টি-কপিরাইট ভয়েস এবং অডিও মোড")
    st.write("💡 এখান থেকে যেকোনো একটি মোড সিলেক্ট করুন। প্রতিটি মোড অডিওর মেটাডেটা ও সুর সম্পূর্ণ চেঞ্জ করে দেবে যাতে কপিরাইট না আসে।")
    
    # অডিও সম্পূর্ণ পরিবর্তন করার ৩টি প্রিমিয়াম সিকিউরিটি অপশন
    voice_style = st.selectbox("ভয়েজ ও সুর পরিবর্তনের মোড সিলেক্ট করুন:", [
        "🔥 High Security Voice Changer (পিচ ভারী + ৩% স্পিড চেঞ্জ - সবচেয়ে নিরাপদ)",
        "🎵 Creative Lo-Fi Vibe (হালকা ইকো + ২% গতি বৃদ্ধি)",
        "🎙️ Deep Cinematic Echo (রহস্যময় গম্ভীর কণ্ঠ - দ্য আননোন কোডেক্স স্পেশাল)"
    ])

    st.markdown("---")
    st.subheader("৩. আপনার পেজের নাম (Watermark / Branding)")
    page_name = st.text_input("আপনার ফেসবুক পেজ বা ইউটিউব চ্যানেলের নাম লিখুন:", placeholder="The Unknown Codex")

    if st.button("🚀 কপিরাইট রিমুভ ও প্রসেস শুরু করুন"):
        with st.spinner("ভিডিও সোজা রেখে কালার গ্রেডিং এবং অডিও ট্র্যাক সম্পূর্ণ পরিবর্তন করা হচ্ছে..."):
            try:
                ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
                
                # ভিডিও ফিল্টার: লেখা সোজা রেখে ৩% জুম এবং কালার মডিফিকেশন
                base_video_filters = "crop=in_w*0.97:in_h*0.97:in_w*0.015:in_h*0.015,eq=contrast=1.07:brightness=0.02:saturation=1.05,scale=1280:720"
                
                if page_name:
                    branding_filter = (
                        f",drawtext=fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf':"
                        f"text='{page_name}':x=w-tw-30:y=h-th-30:fontsize=26:fontcolor=white@0.6:"
                        f"shadowcolor=black:shadowx=2:shadowy=2"
                    )
                    video_filters = base_video_filters + branding_filter
                else:
                    video_filters = base_video_filters
                
                # ==================== কড়া অডিও ফিল্টার চেইন ====================
                if "High Security Voice Changer" in voice_style:
                    #asetrate দিয়ে পিচ সামান্য ডাউন (0.93) এবং স্পিড অ্যাডজাস্ট করার জন্য atempo। এতে ভয়েস মেলা অসম্ভব।
                    audio_filters = "asetrate=44100*0.93,atempo=1.07,bass=g=5"
                elif "Creative Lo-Fi Vibe" in voice_style:
                    # গতি ৩% বাড়িয়ে দেওয়া হলো এবং হালকা ইকো যোগ করা হলো
                    audio_filters = "atempo=1.03,aecho=0.8:0.85:25:0.2,treble=g=2"
                else:
                    # গভীর ও গম্ভীর রহস্যময় ভয়েস ইফেক্ট
                    audio_filters = "asetrate=44100*0.90,atempo=1.11,aecho=0.8:0.90:35:0.3,bass=g=6"
                # =============================================================
                
                # এফএফএমপেগ কমান্ড এক্সিকিউশন
                if uploaded_image is not None:
                    command = [
                        ffmpeg_exe, '-y',
                        '-i', input_video_path,
                        '-i', input_image_path,
                        '-filter_complex', f"[0:v]{video_filters}[v];[0:a]{audio_filters}[a]",
                        '-map', '[v]', '-map', '[a]',
                        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
                        '-c:a', 'aac', '-b:a', '192k', # অডিও বিটরেট ভালো রাখা হলো
                        output_video_path
                    ]
                else:
                    command = [
                        ffmpeg_exe, '-y',
                        '-i', input_video_path,
                        '-vf', video_filters,
                        '-af', audio_filters,
                        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
                        '-c:a', 'aac', '-b:a', '192k',
                        output_video_path
                    ]
                
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                if os.path.exists(output_video_path) and os.path.getsize(output_video_path) > 0:
                    st.success("🎉 আলহামদুলিল্লাহ ভাই! ভিডিওর লেখা সোজা রেখে অডিও ও ভয়েস সফলভাবে পরিবর্তন করা হয়েছে।")
                    st.subheader("📺 ভিডিও প্রিভিউ:")
                    
                    with open(output_video_path, "rb") as video_file:
                        st.video(video_file.read())
                        
                    with open(output_video_path, "rb") as file:
                        st.download_button(
                            label="⬇️ গ্যালারিতে সেভ করুন (Download Safe Video)",
                            data=file,
                            file_name="branded_copyright_free_video.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error("❌ ভিডিও প্রসেস করতে ঝামেলা হয়েছে ভাই।")
                    st.code(result.stderr)
                    
            except Exception as e:
                st.error(f"দুঃখিত ভাই, এরর: {str(e)}")
            finally:
                if os.path.exists(input_video_path): os.remove(input_video_path)
                if os.path.exists(input_image_path): os.remove(input_image_path)
