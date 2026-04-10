import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(page_title="去水印工具", page_icon="🖼️", layout="wide")

def load_image(uploaded_file):
    bytes_data = uploaded_file.getvalue()
    nparr = np.frombuffer(bytes_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img, cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

def get_mask(img_shape, position):
    h, w = img_shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    
    positions = {
        "居中": (int(w*0.3), int(h*0.4), int(w*0.7), int(h*0.6)),
        "左上": (0, 0, int(w*0.3), int(h*0.15)),
        "左下": (0, int(h*0.85), int(w*0.3), h),
        "右上": (int(w*0.7), 0, w, int(h*0.15)),
        "右下": (int(w*0.7), int(h*0.85), w, h),
        "满屏": (0, 0, w, h)
    }
    
    if position in positions:
        x1, y1, x2, y2 = positions[position]
        mask[y1:y2, x1:x2] = 255
    
    return mask

def remove_watermark(img, mask):
    return cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)

st.title("🖼️ 在线去水印工具")
st.markdown("上传图片 → 选择水印位置 → 一键去除")

uploaded = st.file_uploader("上传图片", type=['jpg', 'jpeg', 'png'])

if uploaded:
    img_bgr, img_rgb = load_image(uploaded)
    st.image(img_rgb, caption="原图", use_column_width=True)
    
    pos = st.selectbox("水印位置", ["居中", "左上", "左下", "右上", "右下", "满屏"])
    
    if st.button("开始去水印"):
        mask = get_mask(img_bgr.shape, pos)
        result = remove_watermark(img_bgr, mask)
        result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        
        st.image(result_rgb, caption="处理结果", use_column_width=True)
        
        _, buf = cv2.imencode('.png', result)
        st.download_button("下载结果", buf.tobytes(), "去水印结果.png", "image/png")
