import streamlit as st
from PIL import Image, ImageEnhance
import numpy as np
import io

# 頁面配置
st.set_page_config(page_title="プロ向け 5色ディザリングツール", layout="wide")

# --- 標題與說明 ---
st.title("🎨 カラー調整機能付き・5色ディザリング")
st.write("特定の色の表示を制限しながら、指定した5色に変換します。")

# --- 側邊欄設定 ---
with st.sidebar:
    st.header("1. 出力カラー設定")
    c1 = st.color_picker("カラー 1", "#000000")
    c2 = st.color_picker("カラー 2", "#FFFFFF")
    c3 = st.color_picker("カラー 3", "#0000FF")
    c4 = st.color_picker("カラー 4", "#00FF00")
    c5 = st.color_picker("カラー 5", "#FFFF00")
    
    st.divider()
    
    st.header("2. 除外したい色の設定 (Rule Out)")
    exclude_color = st.color_picker("除外するターゲット色", "#FF0000") # 預設排除紅色
    threshold = st.slider("除外の強さ (Threshold)", 0, 255, 100)
    st.caption("※選んだ色に近い成分を、処理前に除去します。")
    
    st.divider()
    st.header("3. その他設定")
    use_dither = st.checkbox("ディザリングを有効にする", value=True)

# --- 排除顏色的函數 ---
def rule_out_logic(img, target_hex, threshold):
    # Hex 轉 RGB
    h = target_hex.lstrip('#')
    target_rgb = np.array([int(h[i:i+2], 16) for i in (0, 2, 4)])
    
    data = np.array(img).astype(float)
    # 計算每個像素與目標色的歐幾里得距離
    dist = np.sqrt(np.sum((data - target_rgb)**2, axis=2))
    
    # 建立遮罩：距離小於閥值的像素
    mask = dist < threshold
    
    # 將被排除的顏色轉為灰階，或是強制壓低該色彩成分
    # 這裡採用轉灰階的做法，這樣在之後的 5 色轉換中會被歸類到黑白灰
    grayscale = np.dot(data[mask][...,:3], [0.2989, 0.5870, 0.1140])
    data[mask] = np.stack([grayscale, grayscale, grayscale], axis=-1)
    
    return Image.fromarray(np.uint8(data))

# --- 主要圖片處理 ---
uploaded_file = st.file_uploader("画像をアップロード", type=["jpg", "jpeg", "png"])

if uploaded_file:
    raw_img = Image.open(uploaded_file).convert('RGB')
    
    # 步驟 1: 先執行「排除特定顏色」邏輯
    filtered_img = rule_out_logic(raw_img, exclude_color, threshold)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("除外処理後のプレビュー")
        st.image(filtered_img, use_container_width=True)

    # 步驟 2: 準備 5 色色板
    def hex_to_rgb(h):
        return tuple(int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    
    palette_rgb = []
    for color in [c1, c2, c3, c4, c5]:
        palette_rgb.extend(hex_to_rgb(color))
    
    p_img = Image.new('P', (1, 1))
    p_img.putpalette(palette_rgb + [0] * (768 - len(palette_rgb)))

    # 步驟 3: 執行 5 色轉換與抖動
    dither_mode = Image.FLOYDSTEINBERG if use_dither else Image.NONE
    final_result = filtered_img.quantize(palette=p_img, dither=dither_mode).convert('RGB')

    with col2:
        st.subheader("最終変換結果")
        st.image(final_result, use_container_width=True)
        
        # 下載
        buf = io.BytesIO()
        final_result.save(buf, format="PNG")
        st.download_button("📥 ダウンロード", data=buf.getvalue(), file_name="rule_out_result.png")
