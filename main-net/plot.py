import pandas as pd
import matplotlib.pyplot as plt
from itertools import cycle
import numpy as np

lines = ["k-","k--","k-.","k:"]
linecycler = cycle(lines)

#Load data
df_chain = pd.read_csv('./onchain.csv',sep=',', header=None, names=['Size','Time','Cost'])
df_chain_consecutive = pd.read_csv('./onchain_consecutive.csv',sep=',', header=None, names=['Size','Time','Cost'])
df_offchain = pd.read_csv('./state_channel.csv',sep=',',header=None, names=['Size','Time','Cost'])

x_Size = df_chain['Size']
y1_Time = df_chain['Time']
y2_Time =df_offchain['Time']
y3_Time = df_chain_consecutive['Time']

# Find the intersection point
intersection = np.argwhere(np.diff(np.sign(y1_Time - y2_Time)))[0]

# Coordinates of the intersection point
intersection_x = x_Size[intersection][1]
intersection_y = y1_Time[intersection][1]


plt.plot(x_Size,y1_Time,lines[0],label="On chain solution",marker='o')
plt.plot(x_Size,y2_Time,lines[1],label="Payment channel solution",marker='o')
plt.plot(x_Size,y3_Time,lines[0],label="On chain no-blocking",marker='o')

plt.plot(intersection_x,intersection_y,marker='o',color="red")
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

intersection_x2 = x_Size[intersection][1]
intersection_y2 = y1_Cost[intersection][1]


plt.plot(x_Size,y1_Cost,lines[0],label="On chain solution",marker='o')
plt.plot(x_Size,y2_Cost,lines[1],label="State channel solution",marker='o')
plt.plot(15,15000,marker='^',color="red")
plt.fill_between(x_Size,y1_Cost,y2_Cost,where=(x_Size>intersection_x),interpolate=True,alpha=0.3,color='limegreen')
plt.fill_between(x_Size,y1_Cost,y2_Cost,where=(x_Size<=intersection_x),interpolate=True,alpha=0.3,color='lightsalmon')
plt.ylabel('Cost [\u03BC Algos]')
plt.xlabel('Number of transactions')
plt.grid()
plt.legend()
plt.savefig("plot2.png")
plt.close()


