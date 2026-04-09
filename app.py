import streamlit as st
from PIL import Image
import io

# 頁面配置
st.set_page_config(page_title="レトロ 5色ディザリングツール", layout="wide")

# --- 標題與簡介 ---
st.title("ディザリングツール")
st.write("画像をアップロードして、指定した5色に変換します。")

# --- 側邊欄：色彩與設定 ---
with st.sidebar:
    st.header("カラー設定")
    c1 = st.color_picker("カラー 1", "#000000")
    c2 = st.color_picker("カラー 2", "#FFFFFF")
    c3 = st.color_picker("カラー 3", "#0000FF")
    c4 = st.color_picker("カラー 4", "#00FF00")
    c5 = st.color_picker("カラー 5", "#FFFF00")
    
    st.divider()
    st.header("オプション")
    use_dither = st.checkbox("ディザリング（誤差拡散）を有効にする", value=True)
    st.caption("※有効にすると、色が混ざり合うような質感になります。")

# --- 主要區塊：圖片處理 ---
uploaded_file = st.file_uploader("画像をアップロード (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # 讀取圖片
    raw_img = Image.open(uploaded_file).convert('RGB')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("元の画像")
        st.image(raw_img, use_container_width=True)

    # 1. 準備色板
    def hex_to_rgb(h):
        return tuple(int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

    palette_rgb = []
    for color in [c1, c2, c3, c4, c5]:
        palette_rgb.extend(hex_to_rgb(color))
    
    # 建立色板圖 (P 模式)
    p_img = Image.new('P', (1, 1))
    p_img.putpalette(palette_rgb + [0] * (768 - len(palette_rgb)))

    # 2. 執行處理
    # Image.FLOYDSTEINBERG 為標準誤差擴散算法
    dither_mode = Image.FLOYDSTEINBERG if use_dither else Image.NONE
    processed_img = raw_img.quantize(palette=p_img, dither=dither_mode).convert('RGB')

    with col2:
        st.subheader("変換結果")
        st.image(processed_img, use_container_width=True)
        
        # 3. 下載按鈕
        buf = io.BytesIO()
        processed_img.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.download_button(
            label="📥 変換した画像をダウンロード",
            data=byte_im,
            file_name="dithered_result.png",
            mime="image/png"
        )

# 頁尾說明 (可選)
st.sidebar.info("使い方のヒント: コントラストが高い画像ほど、きれいに仕上がります。")