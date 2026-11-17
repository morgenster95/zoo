import json, os
from PIL import Image
import numpy as np
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..')
meta=json.load(open(f'{ROOT}/web/public/assets/props.json')); atlas=Image.open(f'{ROOT}/web/public/assets/atlas.png').convert('RGBA')
def get(n):
    m=meta[n]; return atlas.crop((m['x'],m['y'],m['x']+m['w'],m['y']+m['h']))
def half(im):
    a=np.array(im); h,w=a.shape[:2]; H,W=(h+1)//2,(w+1)//2
    out=np.zeros((H,W,4),np.uint8)
    for y in range(H):
        for x in range(W):
            blk=a[y*2:y*2+2,x*2:x*2+2].reshape(-1,4); blk=blk[blk[:,3]>0]
            if len(blk)<2: continue
            lum=blk[:,:3].astype(int).sum(1)
            dark=blk[lum<190]
            if len(dark)*2>=len(blk): c=dark[np.argmin(dark[:,:3].astype(int).sum(1))]
            else:
                q=(blk[:,:3]//24); keys,inv,cnt=np.unique(q,axis=0,return_inverse=True,return_counts=True)
                k=np.argmax(cnt); c=blk[np.where(inv.ravel()==k)[0][0]]
            out[y,x]=(*c[:3],255)
    return Image.fromarray(out)
if __name__=='__main__':
    import sys
    import visitors, zoo_art as za
    za.load_style('C_hybrid')
    person=visitors.visitor(visitors.new_spec(11),'SE',0)
    mine=[get(n) for n in ['b_classic','b_modern','b_african','b_asian']]
    full=[get(n) for n in ['bp_cafe','bp_shop','bp_lodge','bp_pagoda','bp_carousel']]
    halves=[half(i) for i in full]
    def strip(ims):
        W=sum(i.width+6 for i in ims)+6; H=max(i.height for i in ims)+10
        s=Image.new('RGBA',(W,H),(104,189,72,255)); x=6
        for i in ims: s.alpha_composite(i,(x,H-i.height-5)); x+=i.width+6
        return s
    rows=[strip([person]+mine),strip([person]+full),strip([person]+halves)]
    W=max(r.width for r in rows); H=sum(r.height for r in rows)
    sh=Image.new('RGBA',(W,H),(104,189,72,255)); y=0
    for r in rows: sh.alpha_composite(r,(0,y)); y+=r.height
    sh.resize((sh.width*4,sh.height*4),Image.NEAREST).save(sys.argv[1]); print(sh.size)
