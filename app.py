import streamlit as st
import subprocess
import os
import imageio_ffmpeg as im_ffmpeg

# বড় ফাইল আপলোডের জন্য সাইজ লিমিট ২০০০ MB করা হলো
st._config.set_option("server.maxUploadSize", 2000)

st.set_page_config(page_title="Smart Video Copyright Remover", page_icon="🛡️", layout="centered")

st.title("🛡️ Smart Video Copyright Remover (Branded Edition)")
st.write("ভিডিও কাটার ঝামেলা ছাড়া, ভয়েজ কপিরাইট বাইপাসিং এবং কাস্টম পেজ ব্র্যান্ডিং সিস্টেম!")

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
    
    # ইনপুট ভিডিও সেভ করা
    with open(input_video_path, "wb") as f:
        f.write(uploaded_video.read())
        
    st.success("✅ ভিডিও সফলভাবে আপলোড হয়েছে ভাই!")
    
    # থাম্বনেইল প্রিভিউ
    if uploaded_image is not None:
        with open(input_image_path, "wb") as f:
            f.write(uploaded_image.read())
        st.image(input_image_path, caption="আপলোড করা থাম্বনেইল", width=300)

    st.markdown("---")
    st.subheader("২. অ্যান্টি-কপিরাইট অডিও সেটআপ")
    
    # ভয়েজ বা সুর পরিবর্তন করার জন্য চমৎকার ড্রপডাউন অপশন
    voice_style = st.selectbox("ভয়েজের ধরন পরিবর্তন করুন (কপিরাইট বাইপাস করার জন্য):", [
        "Deep Cinematic Voice (কণ্ঠ একটু ভারী ও রহস্যময় করা)",
        "Slightly Fast Lo-Fi Mood (গতি সামান্য বাড়িয়ে কপিরাইট মুক্ত করা)",
        "Soft Pitch Shift (হালকা রোবোটিক ফিল্টার - সেফেস্ট অপশন)"
    ])

    st.markdown("---")
    st.subheader("৩. আপনার পেজের নাম (Watermark / Branding)")
    # এখানে আপনি আপনার পেজের নাম ইনপুট দিতে পারবেন ভাই
    page_name = st.text_input("আপনার ফেসবুক পেজ বা ইউটিউব চ্যানেলের নাম লিখুন (ভিডিওর কোণায় থাকবে):", 
                             placeholder="The Unknown Codex")

    if st.button("🚀 কপিরাইট রিমুভ ও ব্র্যান্ডেড ভিডিও তৈরি করুন"):
        with st.spinner("ভিডিও মডিফাই এবং পেজের নাম যুক্ত হচ্ছে... একটু অপেক্ষা করুন ভাই..."):
            try:
                ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
                
                # স্ক্রিন মিররিং ও কালার গ্রেডিং ফিল্টার
                base_video_filters = "hflip,eq=contrast=1.05:brightness=0.02:saturation=1.03,scale=1280:720"
                
                # পেজের নাম লেখার বক্সে কিছু থাকলে তা ভিডিওর নিচের ডান কোণায় (W-w-20 : H-h-20) যোগ হবে
                if page_name:
                    # এফএফএমপেগ এর ড্রটেক্সট (drawtext) ফিল্টার ব্যবহার করে ফন্ট বসানো
                    # লিনাক্স সার্ভারের স্ট্যান্ডার্ড বোল্ড ফন্ট ব্যবহার করা হয়েছে, সাইজ ২৪, সাদা রঙ, হালকা শ্যাডো
                    branding_filter = (
                        f",drawtext=fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf':"
                        f"text='{page_name}':x=w-tw-30:y=h-th-30:fontsize=26:fontcolor=white@0.6:"
                        f"shadowcolor=black:shadowx=2:shadowy=2"
                    )
                    video_filters = base_video_filters + branding_filter
                else:
                    video_filters = base_video_filters
                
                # ইউজারের সিলেক্ট করা অপশন অনুযায়ী ভয়েজ ফিল্টার সেটআপ
                if "Deep Cinematic Voice" in voice_style:
                    audio_filters = "asetrate=44100*0.95,atempo=1.05,bass=g=4"
                elif "Slightly Fast Lo-Fi Mood" in voice_style:
                    audio_filters = "atempo=1.03,aecho=0.8:0.88:30:0.2"
                else:
                    audio_filters = "asetrate=44100*1.02,atempo=0.98"
                
                # এফএফএমপেগ কমান্ড তৈরি
                if uploaded_image is not None:
                    command = [
                        ffmpeg_exe, '-y',
                        '-i', input_video_path,
                        '-i', input_image_path,
                        '-filter_complex', f"[0:v]{video_filters}[v];[0:a]{audio_filters}[a]",
                        '-map', '[v]', '-map', '[a]',
                        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '24',
                        '-c:a', 'aac', '-b:a', '128k',
                        output_video_path
                    ]
                else:
                    command = [
                        ffmpeg_exe, '-y',
                        '-i', input_video_path,
                        '-vf', video_filters,
                        '-af', audio_filters,
                        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '24',
                        '-c:a', 'aac', '-b:a', '128k',
                        output_video_path
                    ]
                
                # কমান্ড রান করা
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                if os.path.exists(output_video_path) and os.path.getsize(output_video_path) > 0:
                    st.success("🎉 আলহামদুলিল্লাহ ভাই! আপনার ব্র্যান্ডেড কপিরাইট-ফ্রি ভিডিও সফলভাবে তৈরি হয়েছে।")
                    st.subheader("📺 ভিডিও প্রিভিউ:")
                    
                    with open(output_video_path, "rb") as video_file:
                        st.video(video_file.read())
                        
                    with open(output_video_path, "rb") as file:
                        st.download_button(
                            label="⬇️ গ্যালারিতে সেভ করুন (Download Branded Video)",
                            data=file,
                            file_name="branded_copyright_free.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error("❌ প্রсеসিং এ কোনো সমস্যা হয়েছে।")
                    st.code(result.stderr)
                    
            except Exception as e:
                st.error(f"দুঃখিত ভাই, ইন্টারনাল এরর: {str(e)}")
            finally:
                if os.path.exists(input_video_path): os.remove(input_video_path)
                if os.path.exists(input_image_path): os.remove(input_image_path)
