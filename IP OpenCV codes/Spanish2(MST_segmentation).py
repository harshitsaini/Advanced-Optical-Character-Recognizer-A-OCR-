import cv2
import math
import numpy as np
from PIL import Image
from pytesseract import *

src_path= 'C://Users//Harshit//Desktop//Initial_img//Machine Printed//Spanish2//mst_seg//'

def getThresholded(img,smooth_it):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if smooth_it==True:
        kernel = np.ones((7, 7), np.float32) / 49
        smooth = cv2.filter2D(img, -1, kernel)
        cv2.imwrite(src_path + "smoothened.png", smooth)
        img=smooth
    # ret, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    #threshed = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 121, 2)
    #img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY, 11, 2)
    #cv2.imwrite(src_path + 'thresholded.png',threshed)
    return img

def getClosed(img,iterations,kernel_size):
    kernel = np.ones((kernel_size,kernel_size), np.uint8)
    k = iterations
    closed=img
    while (k != 0):
        closed = cv2.morphologyEx(closed, cv2.MORPH_CLOSE, kernel)
        k -= 1
    cv2.imwrite(src_path + "closed.png", closed)
    return closed

def getOpened(img,iterations,kernel_size):
    kernel = np.ones((kernel_size,kernel_size), np.uint8)
    k = iterations
    opened=img
    while (k != 0):
        opened = cv2.morphologyEx(opened, cv2.MORPH_OPEN, kernel)
        k -= 1
    cv2.imwrite(src_path + "opened.png", opened)
    return opened

def getMorph(img,iterations,kernel_size,erode_it):
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    if erode_it == True :
        eroded = cv2.erode(img, kernel, iterations=iterations)
        cv2.imwrite(src_path + 'eroded.png', eroded)
        return eroded
    else:
        dilated= cv2.dilate(img, kernel, iterations=iterations)
        cv2.imwrite(src_path + "dilated.png", dilated)
        return dilated

def img_show(*args):
    for it,value in enumerate(args):
        cv2.imshow('Image Number: '+str(it),value)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

class disjoint_set:
    def __init__(self):
        self.parent= -1
        self.rank=0

class edge:
    def __init__(self):
        self.u=-1
        self.v=-1
        self.w=-1

def find_parent(dset,i):
    if dset[i].parent==-1:
        return i
    return find_parent(dset, dset[i].parent)

def dsUnion(dset,x,y):
    xroot=find_parent(dset,x)
    yroot=find_parent(dset,y)
    if dset[xroot].rank >= dset[yroot].rank:
        dset[yroot].parent = xroot
        dset[xroot].rank += 1
    else :
        dset[xroot].parent = yroot
        dset[yroot].rank += 1

graph=2000000*[]
#visited=[]
tree=[]
class Point:
    '''def __init__(self):
        self.x = 0;
        self.y = 0;
        self.val = 0'''
    def __init__(self,*args):
        if len(args)==0:
            self.x = 0; self.y = 0;  self.val = 0

        elif len(args)==2:
            self.val=args[0]
            self.width=args[1]
            self.y = self.val / self.width
            self.x = self.val % self.width

        else:
            self.x=args[0]
            self.y=args[1]
            self.width= args[2]
            self.val = self.y * self.width + self.x


def dfs(u,p):
    tree.append(u)
    for v in graph[u]:
        if v!=p:
            dfs(v,u)


# get subtrees in the given forest
def getIslands(spanned):
   n= len(spanned)
   graph= (n+1)*[]
   make_graph(spanned)
   forest=[]

   for u in range(n+1):
       tree=[]
       dfs(u,-1)
       forest.append(tree)

   return forest

def make_graph(edges):
    print('No of edges'+str(len(edges)))
    for eg in edges:
        graph[eg[0]].append(eg[1])
        graph[eg[1]].append(eg[0])

def getMST(edges,n):
    edges.sort(key=lambda item: item.w)
    for i in range(20):
        print(str(edges[i].u)+' '+str(edges[i].v)+' '+str(edges[i].w))

    mst=[] ; st=0
    dset = [disjoint_set() for i in range(n)]
    kt=0
    for it in range(n):
        kt+=1
        while (find_parent(dset,edges[st].u)==find_parent(dset,edges[st].v) and (st<n)): st+=1
        if(st>=n): break
        x = edges[st].u ; y = edges[st].v ;   wt = edges[st].w
        dsUnion(dset,x,y)
        mst.append([x,y]) ; st+=1
    print('ok '+str(len(mst))+' '+str(kt))
    return mst

def getSpannedTrees(img):
    height, width = img.shape
    n= height*width ; m=0
    edges = [edge() for i in range(n*4)]
    for yt in range(height-1):
        for xt in range(width):
            w = abs(img[yt,xt]-img[yt+1,xt])
            p1 = Point(xt,yt,width)
            p2 = Point(xt,yt+1,width)
            u=p1.val; v= p2.val
            edges[m].u = u; edges[m].v = v;
            edges[m].w = w;  m += 1
    for xt in range(width-1):
        for yt in range(height):
            w = abs(img[yt, xt] - img[yt, xt+1])
            p1 = Point(xt,yt,width)
            p2 = Point(xt+1,yt,width)
            u=p1.val; v= p2.val
            edges[m].u = u; edges[m].v = v;
            edges[m].w = w;  m += 1
    print('DONE '+str(m))
    mst = getMST(edges[0:m], n)
    print(len(mst))
    return mst


def make_it_work():
    img= cv2.imread(src_path+'span2_img.png')
    thresh=getThresholded(img,False)
    spanned= getSpannedTrees(thresh)
    print('Spanned edges: '+str(len(spanned)))
    forest=getIslands(spanned)
    print(len(forest))
    print(forest)

make_it_work()