import pandas as pd
import matplotlib.pyplot as plt
from itertools import cycle
import numpy as np


def calculate_line_equation(x1, y1, x2, y2):
    m = (y2 - y1) / (x2 - x1)
    b = y1 - m * x1
    return m, b

def find_intersection_point(m1, b1, m2, b2):
    x_intersection = (b2 - b1) / (m1 - m2)
    y_intersection = m1 * x_intersection + b1
    return x_intersection, y_intersection


lines = ["k-","k--","k-.","k:"]
linecycler = cycle(lines)

#Load data
df_chain = pd.read_csv('./onchain.csv',sep=',', header=None, names=['Size','Time','Cost'])
df_chain_consecutive = pd.read_csv('./onchain_consecutive.csv',sep=',', header=None, names=['Size','Time','Cost'])
df_offchain = pd.read_csv('./state_channel.csv',sep=',',header=None, names=['Size','Time','Cost'])

x_Size = np.array(df_chain['Size'].to_list())
y1_Time = np.array(df_chain['Time'].to_list())
y2_Time =np.array(df_offchain['Time'].to_list())
y3_Time = np.array(df_chain_consecutive['Time'].to_list())

# Find the intersection point
intersection = np.argwhere(np.diff(np.sign(y1_Time - y2_Time)))[0,0]

# Coordinates of the intersection point
intersection_x = x_Size[intersection]
intersection_y = y1_Time[intersection]
print(y3_Time)

x1,y1 = x_Size[4],y3_Time[4]
x2,y2 = x_Size[5],y3_Time[5]

x3,y3 = x_Size[4],y2_Time[4]
x4,y4 = x_Size[5],y2_Time[5]

# Calculate the equations of the lines
m1, b1 = calculate_line_equation(x1, y1, x2, y2)
m2, b2 = calculate_line_equation(x3, y3, x4, y4)

# Find the intersection point
x_intersection, y_intersection = find_intersection_point(m1, b1, m2, b2)
print(x_intersection,y_intersection)

plt.plot(x_Size, y1_Time, marker='o', label="On-chain solution", color='blue')
plt.plot(x_Size, y2_Time, marker='o', label="Payment channel solution", color='orange')
plt.plot(x_Size, y3_Time, marker='o', label="On-chain no-blocking", color='purple')


plt.plot(intersection_x,intersection_y,marker='o',color="red")
plt.plot(x_intersection,y_intersection,marker='o',color="red")

plt.fill_between(x_Size,y1_Time,y2_Time,where=(x_Size>intersection_x),interpolate=True,alpha=0.3,color='limegreen')
plt.fill_between(x_Size,y1_Time,y2_Time,where=(x_Size<intersection_x),interpolate=True,alpha=0.3,color='lightsalmon')
plt.ylabel('Time [sec]')
plt.xlabel('Number of transactions')
plt.grid()
plt.legend()
plt.savefig("plot3.png")
plt.close()


y1_Cost=df_chain['Cost']
y2_Cost=df_offchain['Cost']

# Find the intersection point
intersection = np.argwhere(np.diff(np.sign(y1_Cost - y2_Cost)))[0]

intersection_x2 = x_Size[intersection]
intersection_y2 = y1_Cost[intersection]


plt.plot(x_Size,y1_Cost,lines[0],label="On chain solution",marker='o')
plt.plot(x_Size,y2_Cost,lines[1],label="Payment channel solution",marker='o')
plt.plot(15,15000,marker='o',color="red")
plt.fill_between(x_Size,y1_Cost,y2_Cost,where=(x_Size>intersection_x),interpolate=True,alpha=0.3,color='limegreen')
plt.fill_between(x_Size,y1_Cost,y2_Cost,where=(x_Size<=intersection_x),interpolate=True,alpha=0.3,color='lightsalmon')
plt.ylabel('Cost [\u03BC Algos]')
plt.xlabel('Number of transactions')
plt.text(10,20000, r'BEP', fontsize=12, color='red')
plt.plot([15, 15], [0, 15000], color='black', linestyle='dotted', dashes=(2, 2))
plt.grid()
plt.legend()
# Adjust layout to make room for labels
plt.tight_layout()
plt.savefig("plot2.png")
plt.close()


