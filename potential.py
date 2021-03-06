"""
Potential Field based path planner
author: Atsushi Sakai (@Atsushi_twi)
Ref:
https://www.cs.cmu.edu/~motionplanning/lecture/Chap4-Potential-Field_howie.pdf
"""

import numpy as np
from scipy import arange
import matplotlib.pyplot as plt

# Parameters
KP = 5.0  # attractive potential gain
ETA = 100.0  # repulsive potential gain
AREA_WIDTH = 30.0  # potential area width [m]

show_animation = True


def calc_potential_field(gx, gy, ox, oy, reso, rr):
    minx = min(ox) - AREA_WIDTH / 2.0
    miny = min(oy) - AREA_WIDTH / 2.0
    maxx = max(ox) + AREA_WIDTH / 2.0
    maxy = max(oy) + AREA_WIDTH / 2.0
    xw = int(round((maxx - minx) / reso))
    yw = int(round((maxy - miny) / reso))

    # calc each potential
    pmap = [[0.0 for i in range(yw)] for i in range(xw)]

    for ix in range(xw):
        x = ix * reso + minx

        for iy in range(yw):
            y = iy * reso + miny
            ug = calc_attractive_potential(x, y, gx, gy)
            uo = calc_repulsive_potential(x, y, ox, oy, rr)
            uf = ug + uo
            pmap[ix][iy] = uf

    return pmap, minx, miny


def calc_attractive_potential(x, y, gx, gy):
    return 0.5 * KP * np.hypot(x - gx, y - gy)


def calc_repulsive_potential(x, y, ox, oy, rr):
    # search nearest obstacle
    minid = -1
    dmin = float("inf")
    for i, _ in enumerate(ox):
        d = np.hypot(x - ox[i], y - oy[i])
        if dmin >= d:
            dmin = d
            minid = i

    # calc repulsive potential
    dq = np.hypot(x - ox[minid], y - oy[minid])

    if dq <= rr:
        if dq <= 0.1:
            dq = 0.1

        return 0.5 * ETA * (1.0 / dq - 1.0 / rr) ** 2
    else:
        return 0.0


def get_motion_model():
    # dx, dy
    motion = [[1, 0],
              [0, 1],
              [-1, 0],
              [0, -1],
              [-1, -1],
              [-1, 1],
              [1, -1],
              [1, 1]]

    return motion


def potential_field_planning(sx, sy, gx, gy, ox, oy, reso, rr):

    # calc potential field
    pmap, minx, miny = calc_potential_field(gx, gy, ox, oy, reso, rr)

    # search path
    d = np.hypot(sx - gx, sy - gy)
    ix = round((sx - minx) / reso)
    iy = round((sy - miny) / reso)
    gix = round((gx - minx) / reso)
    giy = round((gy - miny) / reso)

    if show_animation:
        draw_heatmap(pmap)
        plt.plot(ix, iy, "*k")
        plt.plot(gix, giy, "*m")

    rx, ry = [sx], [sy]
    motion = get_motion_model()
    ls = list()
    while d >= reso:
        minp = float("inf")
        minix, miniy = -1, -1
        for i, _ in enumerate(motion):
            inx = int(ix + motion[i][0])
            iny = int(iy + motion[i][1])
            if inx >= len(pmap) or iny >= len(pmap[0]):
                p = float("inf")  # outside area
            else:
                p = pmap[inx][iny]
            if minp > p:
                minp = p
                minix = inx
                miniy = iny
        ix = minix
        iy = miniy
        xp = ix * reso + minx
        yp = iy * reso + miny
        d = np.hypot(gx - xp, gy - yp)
        rx.append(xp)
        ry.append(yp)


        if show_animation:
            plt.plot(ix, iy, ".y")
            thistuple = (ix,iy)
            ls.append(thistuple)
            #print('('+str(ix)+','+str(iy)+')')


    print("Goal!!")
    print(ls)
    return rx, ry


def draw_heatmap(data):
    data = np.array(data).T
    plt.pcolor(data, vmax=1000.0, cmap=plt.cm.Blues)


def main():
    print("potential_field_planning start")

    sx = 0.0  # start x position [m]
    sy = 0.0  # start y positon [m]
    gx = 69.0  # goal x position [m]
    gy = 60.0  # goal y position [m]
    grid_size = 0.5  # potential grid size [m]
    robot_radius = 2.0  # robot radius [m]


    ox = [(40.5-39),40.5,(40+39),40.5,40.5,40.5,40,41,40.5,15.0, 05.0, 20.0, 25.0,32.0]  # obstacle x position list [m]
    oy = [40,(40+39),40.5,(40.5-39),1.0,2.0,1.5,1.5,1.5,25.0, 15.0, 26.0, 25.0,32.0]  # obstacle y position list [m]
    for i in arange((40.5-4.5*1.44),40.5,0.5):
        ox.append(i)
        oy.append((81-4.5*1.44)-i)
    for i in arange((40.5-4.5*1.44),40.5,0.5):
        ox.append(i)
        oy.append((i+4.5*1.44))
    for i in arange((40.5),(40.5+4.5*1.44),0.5):
        ox.append(i)
        oy.append(81+4.5*1.44-i)
    for i in arange((40.5),(40.5+4.5*1.44),0.5):
        ox.append(i)
        oy.append(i-4.5*1.44)
    for i in range(81):
        ox.append(i)
        oy.append(0.0)
    for i in range(81):
        ox.append(81)
        oy.append(i)
    for i in range(81):
        ox.append(0.0)
        oy.append(i)
    for i in range(81):
        ox.append(i)
        oy.append(81.0)
    if show_animation:
        plt.grid(True)
        plt.axis("equal")

    # path generation
    _, _ = potential_field_planning(
        sx, sy, gx, gy, ox, oy, grid_size, robot_radius)
    if show_animation:
        plt.show()
if __name__ == '__main__':
    print(__file__ + " start!!")
    main()
    print(__file__ + " Done!!")
