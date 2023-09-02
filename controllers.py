import os
from fastapi import FastAPI
from starlette.requests import Request
from modules.ai_talk import AITalkWebAPI
import sqlite3
 
app = FastAPI(
    title='spajam チームアンリミテッドエグゾディア',
    description='プロジェクト名は未定です',
    version='0.9 beta'
)
 
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

@app.get("/user/create")
def user_create(user_name: str):
  dbname = 'spajam.db'
  conn = sqlite3.connect(dbname)
  cur = conn.cursor()
  cur.execute('INSERT INTO persons(name) values("Taro")')
  conn.commit()
  cur.close()
  conn.close()

