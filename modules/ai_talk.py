#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import urllib.error
import urllib.parse
import urllib.request


OUTPUT_FILE = './test.mp3'
OUTPUT_EXT = os.path.splitext(OUTPUT_FILE)[1][1:].lower()


class AITalkWebAPI:
	"""AITalk WebAPIを扱うクラス"""

	URL = 'https://webapi.aitalk.jp/webapi/v5/ttsget.php'	# WebAPI URL

	#  【通知されたものを指定してください】
	ID = "spajam2023"	# ユーザ名(接続ID)
	PW = 'gGLgPWBp'	# パスワード(接続パスワード)


	def __init__(self):
		"""コンストラクタ"""
		# 合成パラメータ（詳細はWebAPI仕様書を参照）
		self.username = self.ID
		self.password = self.PW
		self.speaker_name 	= 'nozomi_emo'	# 話者名
		self.style 			= '{"j":"1.0"}'	# 感情パラメータ
		self.input_type 	= 'text'		# 合成文字種別
		self.text 			= ''			# 合成文字
		self.volume 		= 1.0			# 音量（0.01-2.00）
		self.speed 			= 1.0			# 話速（0.50-4.00）
		self.pitch 			= 1.0			# ピッチ（0.50-2.00）
		self.range 			= 1.0			# 抑揚（0.00-2.00）
		self.mvolume 		= 1.0; 			# マスターボリューム（0.01-5.00）
		self.spause 		= 150; 			# 短ポーズ（80-500）
		self.lpause 		= 370; 			# 長ポーズ（100-2000）
		self.epause 		= 800; 			# 文末ポーズ（200-10000）
		self.tpause 		= 0; 			# 終端ポーズ（0-10000）
		self.output_type 	= 'sound'		# 出力形式
		self.ext 			= 'mp3'			# 出力音声形式
		self.use_udic 		= '1'; 			# ユーザー辞書利用フラグ

		# 合成結果データ
		self._headers = None
		self._sound = None
		self._err_msg = None


	def synth(self):
		"""
		音声合成
		@return 正常終了か
		"""
		# 合成パラメータを辞書化
		dic_param = {
			'username'		: self.username,
			'password'		: self.password,
			'speaker_name'	: self.speaker_name,
			'style'			: self.style,
			'input_type'	: self.input_type,
			'text'			: self.text,
			'volume'		: self.volume,
			'speed'			: self.speed,
			'pitch'			: self.pitch,
			'range'			: self.range,
			'mvolume'		: self.mvolume,
			'spause'		: self.spause,
			'lpause'		: self.lpause,
			'epause'		: self.epause,
			'tpause'		: self.tpause,
			'output_type'	: self.output_type,
			'ext'			: self.ext,
			'use_udic'		: self.use_udic
		}

		# URLエンコードされた合成パラメータの生成
		encoded_param = urllib.parse.urlencode(dic_param).encode('ascii')
		# HTTPヘッダーの生成
		header = {'Content-Type': 'application/x-www-form-urlencoded',}
		# URLリクエストの生成
		req = urllib.request.Request(self.URL, encoded_param, header)

		ret = False
		try:
			# URL接続
			with urllib.request.urlopen(req) as response:
				# HTTPステータスコード、ヘッダー、音声データの取得
				self.code = response.getcode()
				self.headers = response.info()
				self.sound = response.read()
				ret = self.code == 200
		except urllib.error.HTTPError as e:
			self._err_msg = 'HTTPError, Code: ' + str(e.code) + ', ' + e.reason
		except urllib.error.URLError as e:
			self._err_msg = e.reason
		return ret

	
	def get_error(self):
		"""
		合成エラーメッセージの取得
		@return 合成エラーメッセージ
		"""
		return self._err_msg if self._err_msg is not None else ''


	def save_to_file(self, output_filepath):
		"""
		音声データのファイル出力
		@param output_filepath 出力ファイルパス
		@return 正常終了か
		"""
		if self.sound is None:
			return False
		
		try:
			with open(output_filepath, 'wb') as f:
				f.write(self.sound)
		except IOError as e:
			return False
		return True


