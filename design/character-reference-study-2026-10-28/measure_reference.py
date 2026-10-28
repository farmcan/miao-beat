"""Reference analysis only. Manual approximate image landmarks, not 3D truth."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib, json, math
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
SRC=ROOT/'public/character/instrument-scenes-v1/guitar/idle.jpg'
im=Image.open(SRC).convert('RGB')
landmarks={
'head_outer_no_ears':[[410,253],[421,202],[436,153],[480,122],[543,113],[608,111],[672,114],[715,133],[741,171],[757,240],[764,288],[762,322],[731,337],[670,342],[584,343],[502,340],[445,333],[398,314]],
'body_visible_outline_clockwise':[[399,322],[351,369],[295,427],[250,477],[216,525],[204,566],[214,596],[191,650],[175,702],[167,759],[173,823],[192,881],[227,928],[280,968],[339,997],[407,1012],[490,1019],[595,1020],[700,1017],[789,1010],[858,993],[912,963],[950,920],[972,869],[978,807],[968,741],[952,682],[936,641]],
'ear_screen_left':[[431,168],[452,105],[461,84],[471,83],[519,121]],
'ear_screen_right':[[655,115],[692,82],[704,77],[713,89],[734,156]],
'right_paw_strumming_screen_left':[[214,523],[252,505],[294,505],[344,520],[391,540],[438,565],[476,588],[502,613],[509,638],[493,660],[462,671],[435,661],[396,641],[347,632],[293,627],[245,616],[217,597],[206,573]],
'left_paw_fretting_screen_right':[[900,550],[902,528],[919,508],[939,486],[959,481],[982,489],[1003,513],[1013,547],[1009,582],[992,617],[970,642],[941,653],[915,642],[900,620],[890,592]],
'eye_screen_left_bbox':[508,183,580,246],
'eye_screen_right_bbox':[649,179,714,244],
'pupil_screen_left_center':[560,218],
'pupil_screen_right_center':[696,214],
'brow_screen_left_curve':[[510,169],[521,159],[538,154],[553,155],[562,160]],
'brow_screen_right_curve':[[657,156],[670,150],[684,151],[698,158],[704,166]],
'nose_bbox':[600,234,645,262],
'muzzle_bbox':[524,243,698,339],
'mouth_curve':[[595,278],[608,285],[624,287],[638,284],[647,277]],
'nose_mouth_line':[[624,258],[624,284]],
'foot_screen_left_bbox':[376,1054,499,1113],
'foot_screen_right_bbox':[696,1054,822,1111],
'guitar_body_visible_outline':[[242,626],[279,614],[320,592],[367,555],[414,538],[456,541],[493,534],[527,507],[559,482],[592,471],[623,474],[654,488],[678,513],[697,545],[715,575],[737,605],[756,640],[771,681],[775,719],[763,750],[737,775],[703,789],[664,793],[628,799],[603,817],[578,844],[551,870],[517,897],[479,919],[437,930],[393,931],[351,921],[312,901],[282,871],[260,838],[245,796],[239,750],[237,703],[242,659]],
'guitar_soundhole_center':[575,652],
'guitar_soundhole_bbox':[517,589,635,716],
'guitar_bridge_center':[391,728],
'guitar_nut_center':[1055,467],
'guitar_axis_guide':[[381,746],[1125,425]],
'guitar_neck_front_corners':[[616,588],[1039,432],[1064,502],[632,662]],
'guitar_headstock_outline':[[1039,432],[1072,403],[1176,365],[1193,373],[1208,410],[1214,433],[1204,451],[1088,494],[1064,502]],
'ground_contact_y':1111,
}
meta={'source':str(SRC.relative_to(ROOT)),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'canvas':[im.width,im.height],'coordinate_convention':'image pixels, origin top-left; x right, y down','measurement_status':'manually read approximate visible 2D landmarks; typically +/- 5-12 px; not a segmentation mask or 3D ground truth','landmarks':landmarks}
(OUT/'landmarks.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
try: font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',20)
except OSError: font=ImageFont.load_default()
canvas=im.copy(); d=ImageDraw.Draw(canvas)
colors={'head_outer_no_ears':'#087dae','body_visible_outline_clockwise':'#d1257f','right_paw_strumming_screen_left':'#065d49','left_paw_fretting_screen_right':'#065d49','guitar_body_visible_outline':'#6839ad','guitar_neck_front_corners':'#6839ad'}
for key,col in colors.items():
    pts=[tuple(p) for p in landmarks[key]]
    d.line(pts if key == 'body_visible_outline_clockwise' else pts+[pts[0]],fill=col,width=4)
    for p in pts:d.ellipse((p[0]-3,p[1]-3,p[0]+3,p[1]+3),fill=col)
for key in ['eye_screen_left_bbox','eye_screen_right_bbox','muzzle_bbox','nose_bbox','foot_screen_left_bbox','foot_screen_right_bbox']:
    d.rectangle(landmarks[key],outline='#087dae',width=3)
for key in ['pupil_screen_left_center','pupil_screen_right_center','guitar_soundhole_center','guitar_bridge_center','guitar_nut_center']:
    x,y=landmarks[key];d.ellipse((x-5,y-5,x+5,y+5),fill='#ef2424');d.text((x+8,y+6),f'{x},{y}',font=font,fill='#122b39',stroke_width=2,stroke_fill='white')
d.line([tuple(p) for p in landmarks['guitar_axis_guide']],fill='#ef2424',width=3)
d.line([(0,1111),(1254,1111)],fill='#999999',width=2)
d.text((25,20),'MANUAL 2D STUDY / APPROXIMATE / NOT A MASK',font=font,fill='#163243',stroke_width=3,stroke_fill='white')
canvas.save(OUT/'reference-landmarks.png')
im.crop((388,70,785,355)).resize((794,570)).save(OUT/'face-reference.png')
im.crop((193,464,1023,688)).save(OUT/'paw-grip-reference.png')
turn=Image.open(ROOT/'design/video-motion-pilot-2026-10-23/01-turnaround.png')
turn.crop((713,23,1337,738)).save(OUT/'turnaround-side-support.png')
turn.crop((1347,23,1974,738)).save(OUT/'turnaround-back-support.png')
print(json.dumps({'written':str(OUT),'axis_angle_degrees':math.degrees(math.atan2(746-425,1125-381)),'source_size':im.size}))
