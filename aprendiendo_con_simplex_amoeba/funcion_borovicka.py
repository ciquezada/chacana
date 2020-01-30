import numpy as np


X0, Y0, a0 = float(724), float(472), float(-3*np.pi/4) #x=724 parece una mejor opcion

def construct_radio(C, A, F):
    def r(x, y):
        return C * ( np.sqrt( (x-X0)**2 + (y-Y0)**2 ) + A*(y-X0)*np.cos(F-a0) - A*(x-X0)*np.sin(F-a0) )
    return r

def construct_u(C, A, F, V, S, D, P, Q):
    def u(x, y):
        r = construct_radio(C, A, F)
        return V*r(x, y) + S*(np.e**(D*r(x,y)) - 1) + P*(np.e**(Q*r(x,y)**2) - 1)
    return u

def construct_b(E):
    def b(x, y):
        return a0 - E + np.arctan2((y - Y0),(x - X0))
    return b

def construct_altura(C, A, F, V, S, D, P, Q, E, ep):
    def z(x, y):
        u = construct_u(C, A, F, V, S, D, P, Q)
        b = construct_b(E)
        return np.arccos( np.cos(u(x,y))*np.cos(ep) - np.sin(u(x,y))*np.sin(ep)*np.cos(b(x,y)) )
    return z

def construct_altura_deg(C, A, F, V, S, D, P, Q, E, ep):
    def z(x, y):
        u = construct_u(C, A, F, V, S, D, P, Q)
        b = construct_b(E)
        return 90 - np.rad2deg( np.arccos( np.cos(u(x,y))*np.cos(ep) - np.sin(u(x,y))*np.sin(ep)*np.cos(b(x,y)) ) )
    return z

def construct_azimuth(C, A, F, V, S, D, P, Q, E, ep):
    def az(x, y):
        u = construct_u(C, A, F, V, S, D, P, Q)
        b = construct_b(E)
        z = construct_altura(C, A, F, V, S, D, P, Q, E, ep)
        return np.arcsin( np.sin(b(x,y))*np.sin(u(x,y))/np.sin(z(x,y)) ) + E
    return az

def construct_azimuth_deg(C, A, F, V, S, D, P, Q, E, ep):
    def az(x, y):
        u = construct_u(C, A, F, V, S, D, P, Q)
        b = construct_b(E)
        z = construct_altura(C, A, F, V, S, D, P, Q, E, ep)
        return np.rad2deg( np.arcsin( np.sin(b(x,y))*np.sin(u(x,y))/np.sin(z(x,y)) ) + E )
    return az
