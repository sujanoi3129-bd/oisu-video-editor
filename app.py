import streamlit as st
import subprocess
import os
import imageio_ffmpeg as im_ffmpeg
from PIL import Image, ImageDraw, ImageFont

# বড় ফাইল আপলোডের জন্য সাইজ লিমিট ২০০০ MB করা হলো
st._config.set_option("server.maxUploadSize", 2000)

st.set_page_config(page_title="Smart Video Copyright Remover", page_icon="🛡️", layout="centered")

st.title("🛡️ Smart Video Copyright Remover (Master Edition)")
st.write("থাম্বনেইল এবং পেজের নাম ভিডিওর ওপরে ১০০% ফুটিয়ে তোলার ফাইনাল ফিক্সড কোড ভাই!")

st.markdown("---")
st.subheader("১. ভিডিও এবং থাম্বনেইল আপলোড করুন")

# ভিডিও ফাইল আপলোড
uploaded_video = st.file_uploader("আপনার মূল ভিডিও ফাইলটি আপলোড করুন (MP4/MKV)", type=["mp4", "mkv"])

# কাস্টম থাম্বনেইল আপলোড (ঐচ্ছিক)
uploaded_image = st.file_uploader("📷 কাস্টম থাম্বনেইল সেটআপ (Optional):", type=["jpg", "jpeg", "png"])

if uploaded_video is not None:
    input_video_path = "temp_input_video.mp4"
    input_image_path = "temp_input_thumb.jpg"
    watermark_path = "temp_watermark.png"
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
    
    voice_style = st.selectbox("ভয়েজ ও সুর পরিবর্তনের মোড সিলেক্ট করুন:", [
        "🔥 High Security Voice Changer (পিচ ভারী + ৩% স্পিড চেঞ্জ - সবচেয়ে নিরাপদ)",
        "🎵 Creative Lo-Fi Vibe (হালকা ইকো + ২% গতি বৃদ্ধি)",
        "🎙️ Deep Cinematic Echo (রহস্যময় গম্ভীর কণ্ঠ)"
    ])

    st.markdown("---")
    st.subheader("৩. আপনার পেজের নাম (Watermark / Branding)")
    page_name = st.text_input("আপনার ফেসবুক পেজ বা ইউটিউব চ্যানেলের নাম লিখুন:", placeholder="ToonFlix")

    if st.button("🚀 কপিরাইট রিমুভ ও ব্র্যান্ডেড ভিডিও তৈরি করুন"):
        with st.spinner("ভিডিও মডিফাই, থাম্বনেইল সেট এবং পেজের নাম ওপরে বসানো হচ্ছে..."):
            try:
                ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
                
                # --- নিখুঁত ওয়াটারমার্ক ইমেজ তৈরি (স্থির সাইজ ১৯২০x১০৮০ দিয়ে করা হলো যাতে সব বড় ভিডিও কভার করে) ---
                if page_name:
                    w_img = Image.new('RGBA', (1920, 1080), (255, 255, 255, 0))
                    draw = ImageDraw.Draw(w_img)
                    
                    try:
                        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 45)
                    except:
                        font = ImageFont.load_default()
                    
                    # ১৯২০x১০৮০ স্ক্রিনের জন্য নিচের দিকে মাঝখানের পজিশন
                    text_x = 960
                    text_y = 1000
                    
                    # ৪ পাশে কালো স্ট্রোক বর্ডার (যাতে লেখা পরিষ্কার বুঝা যায়)
                    for offset in [(-3,-3), (3,-3), (-3,3), (3,3)]:
                        draw.text((text_x + offset[0], text_y + offset[1]), page_name, fill="black", font=font, anchor="mm")
                    # মূল সাদা ওয়াটারমার্ক
                    draw.text((text_x, text_y), page_name, fill=(255, 255, 255, 200), font=font, anchor="mm")
                    w_img.save(watermark_path)
                
                # ভিডিও ফিল্টার চেইন: লেখা সোজা রাখা, ৩% জুম, কালার মিক্স এবং স্ট্যান্ডার্ড ফুল এইচডি স্কেলিং
                video_filters = "crop=in_w*0.97:in_h*0.97:in_w*0.015:in_h*0.015,eq=contrast=1.07:brightness=0.02:saturation=1.05,scale=1920:1080,fps=25"
                
                # অডিও ফিল্টার চেইন
                if "High Security Voice Changer" in voice_style:
                    audio_filters = "asetrate=44100*0.93,atempo=1.07,bass=g=5"
                elif "Creative Lo-Fi Vibe" in voice_style:
                    audio_filters = "atempo=1.03,aecho=0.8:0.85:25:0.2,treble=g=2"
                else:
                    audio_filters = "asetrate=44100*0.90,atempo=1.11,aecho=0.8:0.90:35:0.3,bass=g=6"
                
                # --- এফএফএমপেগ কম্যান্ড মেকিং (ওভারলে সিস্টেম একদম ওপরে রাখার লজিক) ---
                if page_name and os.path.exists(watermark_path):
                    if uploaded_image is not None:
                        # থাম্বনেইল ছবিকেও ১৯২০x১০৮০ সাইজে স্কেল করে ভিডিওর শুরুতে ৫ সেকেন্ডের জন্য ওপরে বসানো হলো
                        command = [
                            ffmpeg_exe, '-y',
                            '-i', input_video_path,
                            '-i', input_image_path,
                            '-i', watermark_path,
                            '-filter_complex', 
                            f"[0:v]{video_filters}[vbase];"
                            f"[1:v]scale=1920:1080[thumb];"
                            f"[vbase][thumb]overlay=enable='lte(t,5)':shortest=0[vthumb];"
                            f"[vthumb][2:v]overlay=0:0:shortest=0[v];[0:a]{audio_filters}[a]",
                            '-map', '[v]', '-map', '[a]',
                            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
                            '-c:a', 'aac', '-b:a', '192k',
                            output_video_path
                        ]
                    else:
                        command = [
                            ffmpeg_exe, '-y',
                            '-i', input_video_path,
                            '-i', watermark_path,
                            '-filter_complex', f"[0:v]{video_filters}[vbase];[vbase][1:v]overlay=0:0:shortest=0[v];[0:a]{audio_filters}[a]",
                            '-map', '[v]', '-map', '[a]',
                            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
                            '-c:a', 'aac', '-b:a', '192k',
                            output_video_path
                        ]
                else:
                    # যদি শুধু থাম্বনেইল থাকে, কোনো পেজের নাম না থাকে
                    if uploaded_image is not None:
                        command = [
                            ffmpeg_exe, '-y',
                            '-i', input_video_path,
                            '-i', input_image_path,
                            '-filter_complex', 
                            f"[0:v]{video_filters}[vbase];"
                            f"[1:v]scale=1920:1080[thumb];"
                            f"[vbase][thumb]overlay=enable='lte(t,5)':shortest=0[v];[0:a]{audio_filters}[a]",
                            '-map', '[v]', '-map', '[a]',
                            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
                            '-c:a', 'aac', '-b:a', '192k',
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
                    st.success("🎉 আলহামদুলিল্লাহ ভাই! এবার ভিডিও মোশন, থাম্বনেইল এবং পেজের নাম—সব একসাথে ১০০% পারফেক্ট হয়েছে।")
                    st.subheader("📺 ভিডিও প্রিভিউ:")
                    
                    with open(output_video_path, "rb") as video_file:
                        st.video(video_file.read())
                        
                    with open(output_video_path, "rb") as file:
                        st.download_button(
                            label="⬇️ গ্যালারিতে সেভ করুন (Download Full Branded Video)",
                            data=file,
                            file_name="final_branded_copyright_free_video.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error("❌ প্রসেস করতে ঝামেলা হয়েছে ভাই। নিচে এরর কোড দেওয়া হলো:")
                    st.code(result.stderr)
                    
            except Exception as e:
                st.error(f"দুঃখিত ভাই, ইন্টারনাল এরর: {str(e)}")
            finally:
                if os.path.exists(input_video_path): os.remove(input_video_path)
                if os.path.exists(input_image_path): os.remove(input_image_path)
                if os.path.exists(watermark_path): os.remove(watermark_path)
