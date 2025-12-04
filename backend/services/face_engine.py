import os
import numpy as np
from deepface import DeepFace
from pathlib import Path
import cv2
from typing import Dict

MODEL = None
MODEL_NAME = "Facenet"
INDEX = {}

# ----------------------------------------------------------
# LOAD FACENET MODEL
# ----------------------------------------------------------
def load_model():
    global MODEL
    if MODEL is None:
        MODEL = DeepFace.build_model(MODEL_NAME)
        print("FaceNet model loaded!")

# ----------------------------------------------------------
# GET EMBEDDING (DeepFace handles detection internally)
# ----------------------------------------------------------
def get_embedding(img):
    try:
        # Convert path → image
        if isinstance(img, (str, Path)):
            img = cv2.imread(str(img))

        # DeepFace internally detects + aligns face → EASY & STABLE
        rep = DeepFace.represent(
            img_path = img,
            model_name = MODEL_NAME,
            enforce_detection = False
        )

        return np.array(rep[0]["embedding"], dtype=np.float32)

    except Exception as e:
        print("Embedding error:", e)
        return None

# ----------------------------------------------------------
# LOAD ALL EMBEDDINGS
# ----------------------------------------------------------
def load_all_embeddings(photos_root: str) -> Dict[str, np.ndarray]:
    photos_root = Path(photos_root)
    embeddings = {}

    for folder in photos_root.iterdir():
        if not folder.is_dir():
            continue

        empid = folder.name
        emb_path = folder / "embedding.npy"

        if emb_path.exists():
            embeddings[empid] = np.load(str(emb_path))
            continue

        # If no embedding.npy, compute from first photo
        for ext in ("*.jpg", "*.jpeg", "*.png"):
            for img_path in folder.glob(ext):
                emb = get_embedding(str(img_path))
                if emb is not None:
                    np.save(emb_path, emb)
                    embeddings[empid] = emb
                    break

    print(f"[Index] Loaded {len(embeddings)} embeddings.")
    return embeddings

# ----------------------------------------------------------
# COSINE MATCHING
# ----------------------------------------------------------
def cosine_sim(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10))

def match_embedding(index: Dict[str, np.ndarray], emb: np.ndarray, threshold=0.75):
    best_emp = None
    best_score = -1

    for empid, ref_emb in index.items():
        score = cosine_sim(ref_emb, emb)
        if score > best_score:
            best_score = score
            best_emp = empid

    if best_score >= threshold:
        return best_emp, best_score

    return None, best_score

# ----------------------------------------------------------
# GENERATE AVERAGE EMBEDDING FOR AN EMPLOYEE
# ----------------------------------------------------------
def generate_employee_embedding(empid, photos_folder):
    folder = Path(photos_folder) / empid
    images = list(folder.glob("*.jpg"))

    if not images:
        return False, "No images found"

    vectors = []
    for img in images:
        emb = get_embedding(str(img))
        if emb is not None:
            vectors.append(emb)

    if not vectors:
        return False, "Could not compute embeddings"

    avg_vec = np.mean(vectors, axis=0)
    avg_vec /= (np.linalg.norm(avg_vec) + 1e-10)

    np.save(folder / "embedding.npy", avg_vec)
    return True, "Embedding saved"

# ----------------------------------------------------------
# BUILD INDEX IN MEMORY
# ----------------------------------------------------------
def build_index(photos_folder: str):
    global INDEX
    INDEX = load_all_embeddings(photos_folder)
    print("[Index] Build complete:", len(INDEX), "employees")
    return INDEX
