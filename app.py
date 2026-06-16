import streamlit as st
import subprocess
import os
import imageio_ffmpeg as im_ffmpeg
from PIL import Image, ImageDraw, ImageFont

# বড় ফাইল আপলোডের জন্য সাইজ লিমিট ২০০০ MB করা হলো
st._config.set_option("server.maxUploadSize", 2000)

st.set_page_config(page_title="Smart Video Copyright Remover", page_icon="🛡️", layout="centered")

st.title("🛡️ Smart Video Copyright Remover (Final Perfection)")
st.write("ভিডিওর সাইজ অটোমেটিক মেপে পেজের নাম একদম স্ক্রিনের ভেতর নিখুঁতভাবে বসানোর ফাইনাল কোড ভাই!")

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
        "🎙️ Deep Cinematic Echo (রহময় গম্ভীর কণ্ঠ)"
    ])

    st.markdown("---")
    st.subheader("৩. আপনার পেজের নাম (Watermark / Branding)")
    page_name = st.text_input("আপনার ফেসবুক পেজ বা ইউটিউব চ্যানেলের নাম লিখুন:", placeholder="Toonflix")

    if st.button("🚀 কপিরাইট রিমুভ ও ব্র্যান্ডেড ভিডিও তৈরি করুন"):
        with st.spinner("ভিডিওর সাইজ মেপে পেজের নাম নিখুঁত পজিশনে বসানো হচ্ছে..."):
            try:
                ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
                
                # --- ট্রিক ১: এফএফএমপেগ দিয়ে ভিডিওর আসল সাইজ (Width & Height) বের করা ---
                probe_command = [
                    ffmpeg_exe, '-i', input_video_path
                ]
                probe_result = subprocess.run(probe_command, stderr=subprocess.PIPE, text=True)
                
                # ডিফল্ট সাইজ ধরে রাখা (যদি ডিটেক্ট করতে না পারে)
                video_w, video_h = 1280, 720
                
                # এফএফএমপেগের আউটপুট থেকে সাইজ খুঁজে বের করার চেষ্টা
                for line in probe_result.stderr.split('\n'):
                    if 'Video:' in line and ',' in line:
                        parts = line.split(',')
                        for part in parts:
                            if 'x' in part and ('[SAR' in part or part.strip().split(' ')[0].replace('x','').isdigit()):
                                try:
                                    dimensions = part.strip().split(' ')[0].split('x')
                                    if len(dimensions) >= 2:
                                        video_w = int(dimensions[0])
                                        video_h = int(dimensions[1])
                                        break
                                except:
                                    pass
                
                # --- ট্রিক ২: ভিডিওর আসল সাইজ অনুযায়ী ওয়াটারমার্ক ছবি তৈরি করা ---
                if page_name:
                    # ভিডিওর এক্সাক্ট সাইজের সমান একটি স্বচ্ছ ছবি তৈরি
                    w_img = Image.new('RGBA', (video_w, video_h), (255, 255, 255, 0))
                    draw = ImageDraw.Draw(w_img)
                    
                    # ভিডিওর সাইজ অনুযায়ী ফন্ট সাইজ মানানসই করা হলো
                    dynamic_font_size = max(18, int(video_w * 0.04)) # চওড়ার ৪% সাইজ হবে ফন্ট
                    
                    try:
                        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", dynamic_font_size)
                    except:
                        font = ImageFont.load_default()
                    
                    # স্ক্রিনের একদম মাঝখানে এবং নিচ থেকে ৮% উপরে টেক্সট পজিশন করা হলো
                    text_x = int(video_w / 2)
                    text_y = int(video_h * 0.92)
                    
                    # কালো স্ট্রোক/বর্ডার (৪ পাশে)
                    for offset in [(-2,-2), (2,-2), (-2,2), (2,2)]:
                        draw.text((text_x + offset[0], text_y + offset[1]), page_name, fill="black", font=font, anchor="mm")
                    # মূল সাদা লেখা
                    draw.text((text_x, text_y), page_name, fill=(255, 255, 255, 180), font=font, anchor="mm")
                    w_img.save(watermark_path)
                
                # ভিডিও ফিল্টার চেইন: লেখা সোজা রেখে ৩% জুম এবং কালার গ্রেডিং
                video_filters = "crop=in_w*0.97:in_h*0.97:in_w*0.015:in_h*0.015,eq=contrast=1.07:brightness=0.02:saturation=1.05,fps=25"
                
                # অডিও ফিল্টার চেইন
                if "High Security Voice Changer" in voice_style:
                    audio_filters = "asetrate=44100*0.93,atempo=1.07,bass=g=5"
                elif "Creative Lo-Fi Vibe" in voice_style:
                    audio_filters = "atempo=1.03,aecho=0.8:0.85:25:0.2,treble=g=2"
                else:
                    audio_filters = "asetrate=44100*0.90,atempo=1.11,aecho=0.8:0.90:35:0.3,bass=g=6"
                
                # এফএফএমপেগ কম্যান্ড এক্সিকিউশন
                if page_name and os.path.exists(watermark_path):
                    if uploaded_image is not None:
                        command = [
                            ffmpeg_exe, '-y',
                            '-i', input_video_path,
                            '-i', input_image_path,
                            '-i', watermark_path,
                            '-filter_complex', f"[0:v]{video_filters}[vbase];[vbase][2:v]overlay=0:0:shortest=0[v];[0:a]{audio_filters}[a]",
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
                    # যদি ওয়াটারমার্ক না থাকে
                    if uploaded_image is not None:
                        command = [
                            ffmpeg_exe, '-y',
                            '-i', input_video_path,
                            '-i', input_image_path,
                            '-filter_complex', f"[0:v]{video_filters}[v];[0:a]{audio_filters}[a]",
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
                    st.success("🎉 আলহামদুলিল্লাহ ভাই! এবার ভিডিও মোশন, সোজা লেখা এবং পেজের নাম—সব একসাথে পারফেক্ট হয়েছে।")
                    st.subheader("📺 ভিডিও প্রিভিউ:")
                    
                    with open(output_video_path, "rb") as video_file:
                        st.video(video_file.read())
                        
                    with open(output_video_path, "rb") as file:
                        st.download_button(
                            label="⬇️ গ্যালারিতে সেভ করুন (Download Branded Video)",
                            data=file,
                            file_name="branded_copyright_free_video.mp4",
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
