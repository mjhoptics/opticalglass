#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np


# In[2]:


import matplotlib.pyplot as plt


# In[3]:


import opticalglass as og
import opticalglass.glassmap as gm
from opticalglass.glassfactory import create_glass


# In[4]:


bk7 = create_glass('N-BK7', 'Schott')
bk7


# In[5]:


str(bk7)


# In[6]:


bk7.glass_code()


# In[7]:


nd = bk7.rindex('d')
nF = bk7.rindex('F')
nC = bk7.rindex('C')
nC, nd, nF


# In[8]:


vd, PFd = og.glass.calc_glass_constants(nd, nF, nC)
nd, vd, PFd


# In[9]:


dFC = nF-nC
vd = (nd - 1.0)/dFC
PFd = (nF-nd)/dFC
nd, vd, PFd


# In[10]:


bk7.rindex(555.0)


# In[11]:


wl = []
rn = []
for i in np.linspace(365., 700., num=75):
    wl.append(i)
    rn.append(bk7.rindex(i))
plt.plot(wl, rn)


# In[12]:


gmf = plt.figure(FigureClass=gm.GlassMapFigure,
                 glass_db=gm.GlassMapDB()).plot()


# In[ ]:




