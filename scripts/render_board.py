"""Render two oblique KiCad views and compose the README image (requires Pillow)."""
from pathlib import Path
import argparse, subprocess
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'docs/images'
def compose():
    width,height,gap,header=1800,2000,40,105
    canvas=Image.new('RGB',(2*width+3*gap,height+header+2*gap),'#edf0f3')
    draw=ImageDraw.Draw(canvas)
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',44)
    for i,side in enumerate(('top','bottom')):
        x=gap+i*(width+gap)
        draw.text((x+36,gap+24),side.title(),font=font,fill='#263445')
        im=Image.open(OUTPUT/f'render-{side}.png').convert('RGBA')
        assert im.width<=width and im.height<=height
        canvas.paste(im,(x+(width-im.width)//2,gap+header+(height-im.height)//2),im)
    canvas.save(OUTPUT/'board-3d-overview.png',optimize=True)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--compose-only',action='store_true');args=parser.parse_args()
    if not args.compose_only:
        for side,rotation in [('top','342,12,348'),('bottom','18,348,12')]:
            subprocess.run(['kicad-cli','pcb','render','--side',side,'--rotate',rotation,
                '--width','1800','--height','2000','--quality','high','--background','transparent',
                '--zoom','0.72','-o',str(OUTPUT/f'render-{side}.png'),str(ROOT/'astra_piNas.kicad_pcb')],check=True,cwd=ROOT)
    compose()
