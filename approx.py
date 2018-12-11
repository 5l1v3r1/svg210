import numpy as np
import matplotlib.pyplot as plt

def quadratic(t, P0, P1, P2):
    return (1-t)*(1-t)*P0 + 2*(1-t)*t*P1 + t*t*P2

def cubic(t, P0, P1, P2, P3):
    return (1-t)*(1-t)*(1-t)*P0 + 3*(1-t)*(1-t)*t*P1 + 3*(1-t)*t*t*P2 + t*t*t*P3

t = np.arange(0., 1., 1./100.)

P0 = np.array([0,0])
P1 = np.array([0,1])
P2 = np.array([1,1])
P3 = np.array([1,0])

PT = cubic(.5, P0,P1,P2,P3)
#PT = .5*(P0+P3)

x = [ cubic(ti, P0,P1,P2,P3)[0] for ti in t ]
y = [ cubic(ti, P0,P1,P2,P3)[1] for ti in t ]

x2 = [ quadratic(ti, P0,P1,PT)[0] for ti in t ]
y2 = [ quadratic(ti, P0,P1,PT)[1] for ti in t ]

fig = plt.figure()

plt.plot(x,y,'ro')
plt.plot(x2,y2, 'go')

plt.show()
