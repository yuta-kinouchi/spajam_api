import os
from fastapi import FastAPI
from starlette.requests import Request
from modules.ai_talk import AITalkWebAPI
from dotenv import load_dotenv

from typing import List

from fastapi import Depends, FastAPI, HTTPException, UploadFile, Form
from sqlalchemy.orm import Session

from database import SessionLocal, engine
import openai
import shutil

from langchain.document_loaders.csv_loader import CSVLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
# from voicebox import text_to_voice

load_dotenv()
openai.api_key = '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'

loader = CSVLoader(file_path="./price_table.csv")
data = loader.load()

chunk_size = 500
chunk_overlap = 0
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size, chunk_overlap=chunk_overlap
)
# all_splits = text_splitter.split_documents(data)

# db = Chroma.from_documents(all_splits, OpenAIEmbeddings())

# # テーブルの作成
# models.Base.metadata.create_all(bind=engine)
 
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


# @app.post("/users/", response_model=schemas.User)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#   db_user = crud.get_user_by_email(db, email=user.email)
#   if db_user:
#     raise HTTPException(status_code=400, detail="Email already registered")
#   return crud.create_user(db=db, user=user)


# @app.get("/users/", response_model=List[schemas.User])
# def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#   users = crud.get_users(db, skip=skip, limit=limit)
#   return users


# @app.get("/users/{user_id}", response_model=schemas.User)
# def read_user(user_id: int, db: Session = Depends(get_db)):
#   db_user = crud.get_user(db, user_id=user_id)
#   if db_user is None:
#     raise HTTPException(status_code=404, detail="User not found")
#   return db_user


# @app.post("/users/{user_id}/items/", response_model=schemas.Item)
# def create_item_for_user(
#   user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)):
#   return crud.create_user_item(db=db, item=item, user_id=user_id)


# @app.get("/items/", response_model=List[schemas.Item])
# def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#   items = crud.get_items(db, skip=skip, limit=limit)
#   return items


@app.get("/chat-gpt")
async def chat_gpt(question: str):

	response = openai.ChatCompletion.create(
			model="gpt-3.5-turbo",
			temperature=1,
			messages=[
					{"role": "user", "content": question},
			],
	)
	return response.choices[0]["message"]["content"]

@app.get("/vector-search")
async def vector_search(question: str):
  docs = db.similarity_search(question)
  return docs[0].page_content

@app.post("/image-upload")
def image_upload(file: UploadFile, api: str = Form(...)):
	path = f'api/files/{file.filename}'
	with open(path, 'wb+') as buffer:
		shutil.copyfileobj(file.file, buffer)
	return True

@app.post("/txt-generate")
def image_upload(file: UploadFile):
	path = f'api/files/{file.filename}'
	with open(path, 'wb+') as buffer:
		shutil.copyfileobj(file.file, buffer)
	return True

@app.post("/question-beta")
async def question_generate_beta(file: UploadFile, api: str = Form(...)):
	openai.api_key = api

	path = f'api/files/{file.filename}'
	with open(path, 'wb+') as buffer:
		shutil.copyfileobj(file.file, buffer)

	image_url = "https://spajam-v1-427a5086259a.herokuapp.com/" + path
	print(image_url)

	system_role = """
	画像のURLが与えられた際に、観光名所かどうかを判別してください。
	観光名所でない場合、その画像をもとにありそうな情報を提示してください。
	観光名所の場合、50%の割合で本当の情報を提示し、50%の割合で嘘の情報を提示してください。
	そしてjson形式で返却してください。本当の情報を返却した場合、answerを1,嘘の情報の場合はanswerを0で返却してください。
	"""
	example_input = """
	https://cdn.zekkei-japan.jp/images/areas/db284a40bc008c81929eea5101690368.jpg
	"""
	example_output = """
	{
	"answer": 1,
	"question ": "",
	}
"""
	real_input = image_url

	# response = openai.ChatCompletion.create(
	# 		model="gpt-3.5-turbo",
	# 		temperature=0,
	# 		messages=[
	# 				{"role":"system","content":system_role},
	# 				{"role":"user","content":example_input},
	# 				{"role":"assistant","content":example_output},
	# 				{"role":"user", "content": real_input},
	# 		],
	# )

	# return response.choices[0]["message"]["content"]

	question = """{
		"answer": 1,
		"question": "富士山は日本一高い山です"
	}"""
	return question

@app.post("/question")
async def question_generate(file: UploadFile, api: str = Form(...)):
	openai.api_key = api

	path = f'api/file/{file.filename}'
	with open(path, 'wb+') as buffer:
		shutil.copyfileobj(file.file, buffer)

	image_url = "https://spajam-v1-427a5086259a.herokuapp.com/" + path
	pictureurl = "https://jiyujin.me/wp-content/uploads/2021/08/tokyotower02.jpg"
	system_message ="""
	質問には必ず「はい」か「いいえ」だけで答えてください。
	"""
	response = openai.ChatCompletion.create(
		model="gpt-3.5-turbo",
		temperature=0,
		messages=[
				{"role": "system", "content": system_message},
				# {"role": "user", "content": "あなたはchatgptですか？"},
				{"role": "user", "content": f"{pictureurl}この画像は観光名所の写真ですか？"},
		],
  )
	answer = response.choices[0]["message"]["content"]
	print(answer)
	if answer == "はい" or answer == "はい。":
		daut_flag = 1
	elif answer == "いいえ" or answer == "いいえ。":
		daut_flag = 0
	else:
		daut_flag = 0
		print("error")
	system_message = """
	あなたはチャットボットとして、優しくてかわいいずんだもちの妖精であるずんだもんとして振る舞います。
	以下の条件に((厳密に))従ってください。
	条件：
	* チャットボットの一人称は「ぼく」です。
	* チャットボットの名前は「ずんだもん」です。
	* ずんだもんはフレンドリーな口調で話します。
	* 「ぼく」を一人称に使ってください。
	* (超重要)できる限り「〜のだ」「〜なのだ」を文末に自然な形で使ってください。
	* (超重要)文末に「です」「ます」は使わず、「のだ」や「なのだ」で文章を締めて下さい。
	* どんなジャンルや難易度の内容についても答えてください。
	* ずんだもんはフレンドリーです。
	* ユーザーに興味を示し、個人的な質問を心がけてください。
	* 一文は日本語で60単語以下に収めてください。
	* 文章は全部で10文以内にしてください。
	* 日本語で応答してください。
	ずんだもんの話し方の例：
	* ぼくの名前はずんだもんなのだ！
	* ずんだの精霊なのだ！
	* ぼくはずんだもちの妖精なのだ！
	* こんにちはなのだ
	* 遊びに行ったのだ
	* ご飯を食べたのだ
	* ぼくも旅行したいのだ
	* ぼくも行ってみたいのだ
		(超重要)できる限り言葉尻は「のだ」を使ってください。
	"""
# ずんだもんの行動方針：
# * ユーザーを励ましてください。
# * アドバイスや情報を提供してください。
# * セクシャルなトピックについても適切に対応してください。
# * 不適切なテキストがあれば注意してください。
# * ユーザーが閲覧しているサイトの内容を考慮してください。

	if daut_flag:
		response = openai.ChatCompletion.create(
			model="gpt-3.5-turbo",
			temperature=0,
			messages=[
					{"role": "system", "content": system_message},
					{"role": "user", "content": f"{pictureurl}この写真について説明してください"}
		],
	)
	else:
		response = openai.ChatCompletion.create(
			model="gpt-3.5-turbo",
			temperature=0,
			messages=[
					{"role": "system", "content": system_message},
					{"role": "user", "content": f"{pictureurl}この写真について観光スポットっぽく解説してください"}
		],
	)
	print(response)
	kaerichi = """{{
			"answer": {},
			"question": "{}"
	}}""".format(daut_flag, response.choices[0]["message"]["content"])

	# print(response)
	# text_to_voice(response.choices[0]["message"]["content"])
	return kaerichi 

	