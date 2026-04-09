import streamlit as st
from PIL import Image
import io

# ページ設定
st.set_page_config(page_title="5色ディザリングツール", layout="wide")

st.title("🎨 5色ディザリングツール")
st.write("表示したい5つの色を選択し、画像をレトロなスタイルに変換します。")

# --- 側邊欄：顯示色設定 ---
with st.sidebar:
    st.header("表示色の設定")
    
    # 定義黃金五色預設值
    # 1. 純黑, 2. 純白, 3. 中灰, 4. 深藍, 5. 金黃
    default_palette = ["#000000", "#FFFFFF", "#808080", "#0000FF", "#FFD700"]
    
    display_colors = []
    for i in range(5):
        # 將預設顏色帶入 value 參數
        c = st.color_picker(f"表示色 {i+1}", default_palette[i], key=f"cp_{i}")
        display_colors.append(c)
    
    st.divider()
    use_dither = st.checkbox("ディザリングを有効にする", value=True)

# --- 核心執行邏輯 ---
uploaded_file = st.file_uploader("画像をアップロードしてください", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # 讀取並轉換為 RGB
    raw_img = Image.open(uploaded_file).convert('RGB')
    
    # 1. 準備色板
    def hex_to_rgb(h):
        return tuple(int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    
    palette_data = []
    for c in display_colors:
        palette_data.extend(hex_to_rgb(c))
    
    # 建立 Pillow P 模式所需的色板圖片（256色，其餘補0）
    p_img = Image.new('P', (1, 1))
    p_img.putpalette(palette_data + [0] * (768 - len(palette_data)))

    # 2. 執行量化與抖動
    dither_mode = Image.FLOYDSTEINBERG if use_dither else Image.NONE
    result = raw_img.quantize(palette=p_img, dither=dither_mode).convert('RGB')

    # 3. 畫面顯示與下載
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("元の画像")
        st.image(raw_img, use_container_width=True)
    with col2:
        st.subheader("変換結果")
        st.image(result, use_container_width=True)
        
        # 下載按鈕
        buf = io.BytesIO()
        result.save(buf, format="PNG")
        st.download_button(
            label="📥 変換した画像をダウンロード",
            data=buf.getvalue(),
            file_name="dither_output.png",
            mime="image/png"
        )
