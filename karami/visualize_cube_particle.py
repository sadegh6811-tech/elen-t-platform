import numpy as np
import matplotlib
matplotlib.use('Agg') # 🛡️ جلوگیری از خطای GUI در ترموکس
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation

# ایجاد شکل و محور سه‌بعدی
fig = plt.figure(figsize=(8, 8), facecolor='black')
ax = fig.add_subplot(111, projection='3d')
ax.set_facecolor('black')

# رسم مکعب (یال‌های آن)
vertices = np.array([[0,0,0], [1,0,0], [1,1,0], [0,1,0],
                     [0,0,1], [1,0,1], [1,1,1], [0,1,1]])
edges = [[0,1],[1,2],[2,3],[3,0],
         [4,5],[5,6],[6,7],[7,4],
         [0,4],[1,5],[2,6],[3,7]]

for edge in edges:
    ax.plot3D(*vertices[edge].T, color='cyan', alpha=0.3, linewidth=1)

# رأس‌ها (نقاط تعادل)
ax.scatter(vertices[:,0], vertices[:,1], vertices[:,2], color='red', s=80, label='Vertices')

# ذره (قیمت)
particle_plot, = ax.plot([0], [0], [0], 'o', color='yellow', markersize=15, label='Particle')

t = 0
def update(frame):
    global t
    t += 0.05
    
    # شبیه‌سازی انرژی (نقدینگی)
    energy = 0.5 + 0.5 * np.sin(t)
    
    if energy < 0.3:
        phase = 'VERTEX (Equilibrium)'
        particle_pos = [0, 0, 0]
        color = 'red'
    elif energy < 0.6:
        phase = 'EDGE (Trend)'
        particle_pos = [energy * 1.5, 0, 0]
        color = 'orange'
    elif energy < 0.85:
        phase = 'FACE (Range)'
        particle_pos = [1, (energy - 0.6) * 2.5, 0]
        color = 'cyan'
    else:
        phase = 'BODY (Chaos)'
        particle_pos = [1, 1, (energy - 0.85) * 5]
        color = 'yellow'
    
    particle_pos = np.clip(particle_pos, 0, 1)
    
    particle_plot.set_data([particle_pos[0]], [particle_pos[1]])
    particle_plot.set_3d_properties([particle_pos[2]])
    particle_plot.set_color(color)
    
    ax.set_title(f'Phase: {phase} | Energy: {energy:.2f}', color='white', fontsize=10)
    return particle_plot,

ax.set_xlabel('Buyer Power', color='cyan')
ax.set_ylabel('Seller Power', color='cyan')
ax.set_zlabel('Time', color='cyan')
ax.tick_params(colors='cyan')
ax.legend(loc='upper right', facecolor='black', edgecolor='cyan', labelcolor='white')

ani = animation.FuncAnimation(fig, update, frames=150, interval=50, blit=False)

# 🚀 ذخیره به صورت GIF (به جای نمایش پنجره)
print("⏳ در حال ساخت انیمیشن سه‌بعدی... (چند لحظه صبر کنید)")
ani.save('cube_particle.gif', writer='pillow', fps=20)
print("✅ انیمیشن با موفقیت در فایل cube_particle.gif ذخیره شد.")
