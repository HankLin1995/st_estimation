import matplotlib.pyplot as plt
from matplotlib.patches import Arc
import numpy as np

def plot_env(x_env,y_env,r):

    center1 = (x_env, y_env-r)
    radius1 = r
    angle1 = 0
    theta1_1 = 270  # 起始角度
    theta1_2 = 90    # 结束角度，逆时针方向

    # 第二个圆弧参数（顶部弧）
    center2 = (x_env, y_env+r)
    radius2 = r
    angle2 = 0
    theta2_1 = 90  # 起始角度
    theta2_2 = 270    # 结束角度，逆时针方向

    # 绘制第一个圆弧（底部弧）
    arc1 = Arc(center1, 2*radius1, 2*radius1, angle=angle1, theta1=theta1_1, theta2=theta1_2, color='gray')
    ax.add_patch(arc1)

    # 绘制第二个圆弧（顶部弧）
    arc2 = Arc(center2, 2*radius2, 2*radius2, angle=angle2, theta1=theta2_1, theta2=theta2_2, color='gray')
    ax.add_patch(arc2)

# 創建圖形和軸
fig, ax = plt.subplots()

# fig.set_size_inches(6, 6)

# 定義多邊形的頂點座標
X0 = 0
Y0 = 0
T =0.35
B = 3
H =1
gap=H/10
LD=-0.2
RD=-0.2
Loc="0+200~0+350"
ARROW_STYLE="<|-|>"

# 繪製多邊形輪廓

x_list = [X0, X0, X0 + T, X0 + T, X0 + T + B, X0 + T + B, X0 + T + B + T, X0 + T + B + T, X0]
y_list = [Y0, Y0 + T + H, Y0 + T + H, Y0 + T, Y0 + T, Y0 + T + H, Y0 + T + H, Y0, Y0]

polygon = plt.Polygon(np.column_stack([x_list, y_list]), closed=True, edgecolor='black', linewidth=2)
ax.add_patch(polygon)

# 填充多邊形內部顏色
ax.fill(x_list, y_list, color='gray')

# 繪製水平方向尺寸線
ax.annotate('', xy=(X0, Y0 + T + H + gap), xytext=(X0 + T, Y0 + T + H + gap), arrowprops=dict(arrowstyle=ARROW_STYLE))
ax.text(X0 + T / 2, Y0 + T + H + 2*gap, f'{T}', fontsize=14, ha='center')

ax.annotate('', xy=(X0 + T, Y0 + T + H + gap), xytext=(X0 + T + B, Y0 + T + H + gap), arrowprops=dict(arrowstyle=ARROW_STYLE))
ax.text(X0 + T + B / 2, Y0 + T + H +  2*gap, f'{B}', fontsize=14, ha='center')

ax.annotate('', xy=(X0 + T + B, Y0 + T + H + gap), xytext=(X0 + T + B + T, Y0 + T + H + gap), arrowprops=dict(arrowstyle=ARROW_STYLE))
ax.text(X0 + T + B + T / 2, Y0 + T + H +  2*gap, f'{T}', fontsize=14, ha='center')

# 繪製垂直方向尺寸線
ax.annotate('', xy=(X0 - gap, Y0), xytext=(X0 - gap, Y0 + T), arrowprops=dict(arrowstyle=ARROW_STYLE))
ax.text(X0 - 3*gap, Y0 + T / 2, f'{T}', fontsize=14, ha='center')

ax.annotate('', xy=(X0 - gap, Y0 + T), xytext=(X0 - gap, Y0 + T + H), arrowprops=dict(arrowstyle=ARROW_STYLE))
ax.text(X0 - 3*gap, Y0 + T + H / 2, f'{H}', fontsize=14, ha='center')

# 樁號主題說明

text_obj = ax.text(X0 + T + B / 2, Y0 - 3*gap, Loc, fontsize=18, ha='center')

line = plt.Line2D([X0 + T, X0 + T + B], [Y0 -3.5*gap, Y0 -3.5*gap], color='black', linewidth=3)
ax.add_line(line)
# line = plt.Line2D([X0 + T, X0 + T + B], [Y0 -0.9, Y0 -0.9], color='black', linewidth=1)
# ax.add_line(line)

# 地形地貌

## 左邊環境

left_depth=0.6

X_ENV=X0-5*gap
Y_ENV=Y0+T+H-left_depth
r=gap/2

ax.text(X_ENV+1*gap, Y_ENV+gap/2, '田',fontproperties='SimSun', fontsize=16, ha='center')
line = plt.Line2D([X_ENV , X_ENV+5*gap], [Y_ENV , Y_ENV ], color='gray', linewidth=1)
ax.add_line(line)

plot_env(X_ENV,Y_ENV,gap/2)

## 右邊環境

right_depth=0

X_ENV=X0+T+B+T+5*gap
Y_ENV=Y0+T+H-right_depth
r=0.1

ax.text(X_ENV-2*gap, Y_ENV+gap/2, '道',fontproperties='SimSun', fontsize=16, ha='center')
line = plt.Line2D([X_ENV , X_ENV-5*gap], [Y_ENV , Y_ENV ], color='gray', linewidth=1)
ax.add_line(line)

plot_env(X_ENV,Y_ENV,gap/2)

# 設置坐標軸
# ax.set_xlim(X0-1,X0+B+T+B+1)
# ax.set_ylim(Y0-1, Y0+B+H+B+1)

# 隱藏坐標軸
ax.axis('off')

# 顯示圖形
# plt.show()
plt.savefig("main.png")
