import streamlit as st
from PIL import Image
import numpy as np
import io

# ページ設定
st.set_page_config(page_title="カラー除外専用ツール", layout="wide")

st.title("🎨 5色カラー除外フィルタ")
st.write("特定の5色を画像から排除（無彩色化）し、レトロな質感に仕上げます。")

# --- 固定の表示色（プログラム内で定義） ---
# ここで最終的な表示色を固定します
FIXED_PALETTE = [
    "#000000", # 黒
    "#FFFFFF", # 白
    "#FF0000", # 赤
    "#0000FF", # 青
    "#FFFF00"  # 黄
]

# --- サイドバー設定 ---
with st.sidebar:
    st.header("除外設定 (Rule Out)")
    st.write("表示させたくない色を5色まで選んでください。")
    
    # 讓客戶選 5 個要排除的顏色
    exclude_colors = []
    for i in range(5):
        default_color = ["#FF0000", "#00FF00", "#FF00FF", "#00FFFF", "#FFA500"][i]
        exclude_colors.append(st.color_picker(f"除外色 {i+1}", default_color))
    
    st.divider()
    use_dither = st.checkbox("ディザリングを有効にする", value=True)
    st.caption("※オンにするとドットの質感がより繊細になります。")

# --- 色彩處理邏輯 ---
def apply_multi_rule_out(img, target_hex_list):
    data = np.array(img).astype(float)
    final_mask = np.zeros(data.shape[:2], dtype=bool)
    
    # 偵測閥值 (可視需求調整敏感度)
    threshold = 80 
    
    for hex_color in target_hex_list:
        h = hex_color.lstrip('#')
        target_rgb = np.array([int(h[i:i+2], 16) for i in (0, 2, 4)])
        dist = np.sqrt(np.sum((data - target_rgb)**2, axis=2))
        final_mask = final_mask | (dist < threshold)
    
    # 將排除色轉為灰階
    grayscale = np.dot(data[final_mask][...,:3], [0.298
