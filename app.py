import streamlit as st
from PIL import Image
import io

# 頁面配置
st.set_page_config(page_title="5色ディザリングツール", layout="wide")

st.title("🎨 5色カラー選択・ディザリングツール")
st.write("最適な5色がプリセットされています。画像をアップロードして変換を開始してください。")

# --- 側邊欄：顯示色設定 ---
with st.sidebar:
    st.header("表示色の設定")
    st.write("画像に使用する5色です（変更も可能です）。")
    
    # 這裡設定了黃金五色預設值
    # 1. 純黑 (暗部)
    # 2. 純白 (亮部)
    # 3. 中灰色 (過渡)
    # 4. 深藍色 (冷色/主題A)
    # 5. 金黃色 (暖色/主題B)
    gold_palette = ["#000000", "#FFFFFF", "#808080", "#0000FF", "#FFD700"]
    
    display_colors = []
    labels = ["極暗 (シャドウ)", "極亮 (ハイライト)", "中間色 (グレー)", "アクセント1 (冷色)", "アクセント2 (暖色)"]
    
    for i in range(5):
        c = st.color_picker(labels[i], gold_palette[i], key=f"cp_{i}")
        display_colors.append(c)
    
    st.divider()
    use_dither = st.checkbox("ディザリングを有効にする", value=True)
    st.info("この5色は、ディテールを最もきれいに再現できるよう最適化されています。")

# --- 執行與顯示 ---
uploaded_file = st.file_uploader("画像をアップロードしてください", type=["jpg", "jpeg", "png"])

if uploaded_file:
    raw_img = Image.open(uploaded_file).convert('RGB')
    
    # 1. 準備色板
    def hex_to_rgb(h):
        return tuple(int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    
    palette_data = []
    for c in display_colors:
        palette_data.extend(hex_to_rgb(c))
    
    p_img = Image.new('P', (1, 1))
    p_img.putpalette(palette_data + [0] * (768 - len(palette_data)))

    # 2. 執行量化與抖動
    dither_mode = Image.FLOYDSTEINBERG if use_dither else Image.NONE
    result = raw_img.quantize(palette=p_img, dither=dither_mode).convert('RGB')

    # 3. 畫面排版
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
