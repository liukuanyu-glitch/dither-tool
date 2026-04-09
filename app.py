import streamlit as st
from PIL import Image
import numpy as np
import io

# 頁面配置
st.set_page_config(page_title="カラー除外ツール", layout="wide")

st.title("🎨 カラー除外・5色ディザリング")
st.write("指定した色を排除し、レトロなスタイルに変換します。")

# --- 固定顯示色（最終輸出的5色） ---
# 這邊固定為經典的復古配色，確保輸出品質穩定
FIXED_PALETTE = ["#000000", "#FFFFFF", "#0000FF", "#00FF00", "#FFFF00"]

# --- 側邊欄：排除色設定 ---
with st.sidebar:
    st.header("除外する色の設定")
    st.write("表示させたくない色（赤、白、オレンジなど）を5つ選んでください。")
    
    exclude_colors = []
    # 預設值可以設為客戶提到的顏色
    defaults = ["#FF0000", "#FFFFFF", "#FFA500", "#00FF00", "#FF00FF"] 
    for i in range(5):
        c = st.color_picker(f"除外色 {i+1}", defaults[i], key=f"ex_{i}")
        exclude_colors.append(c)
    
    st.divider()
    use_dither = st.checkbox("ディザリング（ドット感）を有効にする", value=True)

# --- 核心演算法：精確顏色過濾 ---
def apply_color_exclusion(img, exclude_list):
    data = np.array(img).astype(float)
    final_mask = np.zeros(data.shape[:2], dtype=bool)
    
    # 內部設定一個中等感度的閥值，讓客戶不用自己調
    threshold = 70 
    
    for hex_color in exclude_list:
        h = hex_color.lstrip('#')
        target_rgb = np.array([int(h[i:i+2], 16) for i in (0, 2, 4)])
        # 計算顏色距離
        dist = np.sqrt(np.sum((data - target_rgb)**2, axis=2))
        final_mask = final_mask | (dist < threshold)
    
    # 將排除的顏色區域轉向「中性色」，使其在最終轉換中不顯眼
    data[final_mask] = [128, 128, 128] 
    
    return Image.fromarray(np.uint8(data))

# --- 執行與顯示 ---
uploaded_file = st.file_uploader("画像をアップロード", type=["jpg", "jpeg", "png"])

if uploaded_file:
    raw_img = Image.open(uploaded_file).convert('RGB')
    
    # 1. 執行顏色過濾
    filtered_img = apply_color_exclusion(raw_img, exclude_colors)
    
    # 2. 準備 5 色色板
    def hex_to_rgb(h):
        return tuple(int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    
    palette_data = []
    for c in FIXED_PALETTE:
        palette_data.extend(hex_to_rgb(c))
    
    p_img = Image.new('P', (1, 1))
    p_img.putpalette(palette_data + [0] * (768 - len(palette_data)))

    # 3. 量化與抖動
    d_mode = Image.FLOYDSTEINBERG if use_dither else Image.NONE
    result = filtered_img.quantize(palette=p_img, dither=d_mode).convert('RGB')

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("元の画像")
        st.image(raw_img, use_container_width=True)
    with col2:
        st.subheader("変換結果")
        st.image(result, use_container_width=True)
        
        # 下載
        buf = io.BytesIO()
        result.save(buf, format="PNG")
        st.download_button("📥 変換した画像をダウンロード", data=buf.getvalue(), file_name="output.png")
