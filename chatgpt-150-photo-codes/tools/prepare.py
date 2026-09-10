"""Prepare the base portrait: detect face, crop to 4:5, upscale 2x, build masks.
Outputs go to source/ (crop.jpg + masks/*.png + meta.json)."""
import json, os, sys
import numpy as np, cv2
from PIL import Image, ImageFilter
import mediapipe as mp
from mediapipe.tasks import python as mpp
from mediapipe.tasks.python import vision

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS = os.path.join(ROOT, 'tools', 'models')
SRC = os.path.join(ROOT, 'source')
orig = Image.open(os.path.join(SRC, 'original.jpg')).convert('RGB')
W, H = orig.size

# --- 1. face landmarks on the original to place the crop -------------------
opts = vision.FaceLandmarkerOptions(base_options=mpp.BaseOptions(model_asset_path=os.path.join(MODELS, 'face_landmarker.task')),
                                    num_faces=1, output_face_blendshapes=False)
lm = vision.FaceLandmarker.create_from_options(opts)
res = lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.array(orig)))
pts = np.array([[p.x * W, p.y * H] for p in res.face_landmarks[0]])
fx0, fy0 = pts.min(0); fx1, fy1 = pts.max(0)
fcx, fcy = (fx0 + fx1) / 2, (fy0 + fy1) / 2
print('face box orig', fx0, fy0, fx1, fy1, 'center', fcx, fcy)

# --- 2. crop 4:5 (full height), centred on the face -------------------------
cw = int(round(H * 4 / 5))  # 576
x0 = int(round(fcx - cw / 2)); x0 = max(0, min(W - cw, x0))
crop = orig.crop((x0, 0, x0 + cw, H))
SCALE = 2
crop = crop.resize((cw * SCALE, H * SCALE), Image.LANCZOS)
crop = crop.filter(ImageFilter.UnsharpMask(radius=1.2, percent=45, threshold=2))
crop.save(os.path.join(SRC, 'crop.jpg'), quality=96)
CW, CH = crop.size
print('crop', (x0, 0, x0 + cw, H), '->', crop.size)
arr = np.array(crop)

# --- 3. landmarks on the crop ------------------------------------------------
res = lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=arr))
P = np.array([[p.x * CW, p.y * CH] for p in res.face_landmarks[0]])

def poly_mask(idx, blur=0, dilate=0):
    m = np.zeros((CH, CW), np.uint8)
    cv2.fillPoly(m, [P[idx].astype(np.int32)], 255)
    if dilate: m = cv2.dilate(m, np.ones((dilate, dilate), np.uint8))
    if blur: m = cv2.GaussianBlur(m, (0, 0), blur)
    return m

OVAL = [10,338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,400,377,152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109]
LIPS_OUT = [61,146,91,181,84,17,314,405,321,375,291,409,270,269,267,0,37,39,40,185]
LIPS_IN = [78,95,88,178,87,14,317,402,318,324,308,415,310,311,312,13,82,81,80,191]
EYE_L = [33,7,163,144,145,153,154,155,133,173,157,158,159,160,161,246]
EYE_R = [362,382,381,380,374,373,390,249,263,466,388,387,386,385,384,398]
BROW_L = [70,63,105,66,107,55,65,52,53,46]
BROW_R = [300,293,334,296,336,285,295,282,283,276]

masks = {}
masks['face'] = poly_mask(OVAL, blur=6)
masks['eyes'] = np.maximum(poly_mask(EYE_L, blur=2, dilate=5), poly_mask(EYE_R, blur=2, dilate=5))
masks['mouth'] = poly_mask(LIPS_IN, blur=1.5)               # inner mouth = teeth region
lips = poly_mask(LIPS_OUT, blur=1.5).astype(np.int32) - poly_mask(LIPS_IN).astype(np.int32)
masks['lips'] = np.clip(lips, 0, 255).astype(np.uint8)
masks['brows'] = np.maximum(poly_mask(BROW_L, blur=2, dilate=7), poly_mask(BROW_R, blur=2, dilate=7))
# iris circles
for name, ids in (('iris_l', range(468, 473)), ('iris_r', range(473, 478))):
    c = P[list(ids)].mean(0); r = np.linalg.norm(P[list(ids)[1:]] - c, axis=1).mean()
    m = np.zeros((CH, CW), np.uint8); cv2.circle(m, (int(c[0]), int(c[1])), int(r * 1.05), 255, -1)
    masks[name] = cv2.GaussianBlur(m, (0, 0), 1.5)
masks['iris'] = np.maximum(masks['iris_l'], masks['iris_r'])
# skin = face oval minus eyes/brows/mouth/lips
skin = masks['face'].astype(np.int32) - masks['eyes'] - masks['brows'] - masks['mouth'] - masks['lips']
masks['face_skin'] = np.clip(skin, 0, 255).astype(np.uint8)

# --- 4. selfie segmentation (multiclass) ------------------------------------
sopts = vision.ImageSegmenterOptions(base_options=mpp.BaseOptions(model_asset_path=os.path.join(MODELS, 'selfie_multiclass.tflite')),
                                     output_category_mask=True, output_confidence_masks=True)
seg = vision.ImageSegmenter.create_from_options(sopts)
sres = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=arr))
conf = [np.squeeze(np.array(c.numpy_view())) for c in sres.confidence_masks]  # 0 bg,1 hair,2 body-skin,3 face-skin,4 clothes,5 others
names = ['bg', 'hair', 'body_skin', 'face_skin', 'clothes', 'accessories']
for n, c in zip(names, conf):
    masks['seg_' + n] = (np.clip(c, 0, 1) * 255).astype(np.uint8)
person = 1.0 - conf[0]
# binary selfie segmenter as a second opinion, average them
s2 = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=mpp.BaseOptions(model_asset_path=os.path.join(MODELS, 'selfie_segmenter.tflite')), output_confidence_masks=True))
r2 = s2.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=arr))
c2 = np.squeeze(np.array(r2.confidence_masks[0].numpy_view()))
print('selfie_segmenter mask stats', c2.min(), c2.max(), c2.mean())
# selfie_segmenter's single mask is P(person)
person = np.clip(0.5 * person + 0.5 * c2, 0, 1)
person_u8 = (person * 255).astype(np.uint8)
# refine edges a bit with guided-ish feathering
person_u8 = cv2.GaussianBlur(person_u8, (0, 0), 1.2)
masks['person'] = person_u8
masks['background'] = 255 - person_u8

for k, v in masks.items():
    Image.fromarray(v).save(os.path.join(SRC, 'masks', k + '.png'))

meta = {
    'original_size': [W, H], 'crop_box': [x0, 0, x0 + cw, H], 'scale': SCALE, 'size': [CW, CH],
    'face_box': [float(v) for v in (P[OVAL].min(0).tolist() + P[OVAL].max(0).tolist())],
    'face_center': [float(P[OVAL].mean(0)[0]), float(P[OVAL].mean(0)[1])],
    'eye_l': P[EYE_L].mean(0).tolist(), 'eye_r': P[EYE_R].mean(0).tolist(),
    'mouth': P[LIPS_OUT].mean(0).tolist(), 'nose': P[4].tolist(), 'chin': P[152].tolist(), 'forehead': P[10].tolist(),
}
json.dump(meta, open(os.path.join(SRC, 'meta.json'), 'w'), indent=1)
print(json.dumps(meta, indent=1))

# --- 5. debug sheet -----------------------------------------------------------
dbg = arr.copy().astype(np.float32)
tint = {'person': (0, 255, 0), 'eyes': (0, 200, 255), 'lips': (255, 0, 120), 'mouth': (255, 255, 0), 'iris': (255, 0, 0), 'brows': (150, 80, 255), 'face_skin': (255, 160, 0)}
for k, col in tint.items():
    m = masks[k][..., None] / 255.0 * 0.45
    dbg = dbg * (1 - m) + np.array(col, np.float32) * m
sheet = Image.fromarray(dbg.clip(0, 255).astype(np.uint8)).resize((CW // 2, CH // 2))
segsheet = Image.fromarray(masks['person']).convert('RGB').resize((CW // 2, CH // 2))
out = Image.new('RGB', (CW, CH // 2)); out.paste(sheet, (0, 0)); out.paste(segsheet, (CW // 2, 0))
out.save(os.path.join(ROOT, 'tools', 'debug_masks.jpg'), quality=85)
