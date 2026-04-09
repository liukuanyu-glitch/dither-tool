import streamlit as st
from PIL import Image, ImageOps, ImageEnhance
import numpy as np
import io

# ページ設定
st.set_page_config(page_title="プロ向け カラー最適化ツール", layout="wide")

st.title("🎨 演算最適化版・5色カラーフィルタ")
st.write("大面積の色（壁など）を守りながら、不要な特定色を排除する高度なフィルタです。")

# --- サイドバー設定 (最適化) ---
with st.sidebar:
    st.header("1. 基底色の設定 (守りたい色)")
    # 此顏色為被 Rule Out 的像素會趨向的基底
    base_color_hex = st.color_picker("壁などのベース色", "#FACF4A") # 預設為黃牆顏色
    st.caption("※除外された色は、この基底色に近いトーンに調整されます。")
    
    st.divider()
    
    st.header("2. 除外設定 (Rule Out)")
    # 讓客戶選 5 個要排除的顏色，並加入單獨的閥值控制
    exclude_settings = []
    for i in range(5):
        st.subheader(f"除外色 {i+1}")
        col_c, col_t = st.columns([1, 2])
        default_color = ["#FF0000", "#00FF00", "#FF00FF", "#00FFFF", "#FFA500"][i]
        
        with col_c:
            color = st.color_picker(f"色", default_color, key=f"exc_col_{i}")
        with col_t:
            # 日本術語術：感度（閾値）
            threshold = st.slider(f"感度", 0, 255, 100, key=f"exc_thr_{i}")
            
        exclude_settings.append({"color": color, "threshold": threshold})
    
    st.divider()
    st.header("3. その他調整")
    pre_enhance = st.checkbox("処理前にコントラストを強める", value=True)
    use_dither = st.checkbox("ディザリングを有効にする", value=True)

# --- 最適化された色彩處理邏輯 ---
def hex_to_rgb(h):
    return np.array([int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)])

def apply_optimized_multi_rule_out(img, base_hex, exclude_config):
    # 先對原圖進行對比度增強，有助於區分微小的顏色變化
    if pre_enhance:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.3)
        
    data = np.array(img).astype(float)
    final_mask = np.zeros(data.shape[:2], dtype=bool)
    base_rgb = hex_to_rgb(base_hex).astype(float)
    
    # 建立多個排除遮罩
    for config in exclude_config:
        target_rgb = hex_to_rgb(config["color"]).astype(float)
        # 計算歐幾里得距離
        dist = np.sqrt(np.sum((data - target_rgb)**2, axis=2))
        final_mask = final_mask | (dist < config["threshold"])
    
    # 將排除色「趨向」基底色 (而不是變灰)
    # 我們將這些像素與基底色進行 80% 的混合
    data[final_mask] = data[final_mask] * 0.2 + base_rgb * 0.8
    
    # 確保數值在 0-255
    data = np.clip(data, 0, 255)
    
    return Image.fromarray(np.uint8(data))

# --- 主要執行區塊 ---
uploaded_file = st.file_uploader("画像をアップロードしてください", type=["jpg", "jpeg", "png"])

if uploaded_file:
    raw_img = Image.open(uploaded_file).convert('RGB')
    
    # 步驟 1: 執行 Rule Out
    filtered_img = apply_optimized_multi_rule_out(raw_img, base_color_hex, exclude_settings)
    
    # 步驟 2: 自動生成最優化色板
    # 使用 Image.quantize 並指定 colors=5，Pillow 會動態計算這張圖最完美的 5 色
    # 這比固定色板效果好很多，尤其對於黃牆
    optimized_quant = filtered_img.quantize(colors=5, method=Image.Quantize.FASTOCTREE, dither=Image.NONE)
    
    # 步驟 3: 套用 Dithering
    dither_mode = Image.FLOYDSTEINBERG if use_dither else Image.NONE
    # 將自動色板重新套用到預處理後的圖上
    result = filtered_img.quantize(palette=optimized_quant, dither=dither_mode).convert('RGB')

    # 顯示
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("元の画像")
        st.image(raw_img, use_container_width=True)
    with col2:
        st.subheader("変換結果 (演算最適化版)")
        st.image(result, use_container_width=True)
        
        # 下載
        buf = io.BytesIO()
        result.save(buf, format="PNG")
        st.download_button("📥 変換した画像をダウンロード", data=buf.getvalue(), file_name="dither_optimized.png")

# 專業操作提示 (日文)
st.sidebar.info("""
**操作のヒント:**
1. **基底色の設定**: 壁の最も標準的な黄色をスポイトなどで指定してください。これが全体のトーンを守ります。
2. **除外色と感度**: 例えば「赤色の植木鉢」を消したい場合、色を赤に設定し、感度を少し上げてください。感度を上げすぎると、壁の黄色までグレーに変わってしまうので、プレビューを見ながら微調整してください。
3. **コントラスト**: オンにすると、ディザリングの粒立ちがより鮮明になります。
""")
