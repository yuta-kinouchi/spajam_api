import os
from fastapi import FastAPI
from starlette.requests import Request
from modules.ai_talk import AITalkWebAPI

from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import SessionLocal, engine

# テーブルの作成
models.Base.metadata.create_all(bind=engine)
 
app = FastAPI(
    title='spajam チームアンリミテッドエグゾディア',
    description='プロジェクト名は未定です',
    version='0.9 beta'
)

def get_db():
   db = SessionLocal()
   try:
       yield db
   finally:
       db.close()
 
@app.get("/")
def index(request: Request):
    return {'Hello': 'World'}

@app.get("/ai-talk")
def ai_talk(request: Request):
	"""メイン処理"""

	# (1) 合成内容設定
	target_text = 'こんにちは。今日はいい天気ですね♪'
	target_file = 'output.mp3'	# mp3, ogg, m4a, wav いずれかのファイルパス

	# 出力ファイルから出力形式を決定
	ext = os.path.splitext(target_file)[1][1:]
	if ext == 'm4a':	# m4a拡張子はaacと設定
		ext = 'aac'

	# (2) AITalkWebAPIを使うためのインスタンス作成
	aitalk = AITalkWebAPI()

	# (3) インスタンスに指定したいパラメータをセット
	aitalk.text = target_text
	# aitalk.speaker_name = 'nozomi_emo'
	# aitalk.style = '{"j":"1.0"}'
	aitalk.ext = ext

	# (4) 合成
	if not aitalk.synth():
		# エラー処理
		print(aitalk.get_error(), file=sys.stderr)
		return 1

	# (5) ファイル保存
	if not aitalk.save_to_file(target_file):
		print('failed to save', file=sys.stderr)
		return 1
	return 0


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
   db_user = crud.get_user_by_email(db, email=user.email)
   if db_user:
       raise HTTPException(status_code=400, detail="Email already registered")
   return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
   users = crud.get_users(db, skip=skip, limit=limit)
   return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
   db_user = crud.get_user(db, user_id=user_id)
   if db_user is None:
       raise HTTPException(status_code=404, detail="User not found")
   return db_user


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
   user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
   return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
   items = crud.get_items(db, skip=skip, limit=limit)
   return items