#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lnako 独自命令（低レイヤーAPI: plugin_lowlevel）のドキュメントおよび命令一覧を最新リリースに合わせて生成・更新するスクリプト
"""
import json
import os
import sqlite3

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_PATH = os.path.expanduser('~/Repositories/soramikan/lnako/docs/low-level-api/catalog.json')
DATA_DIR = os.path.join(ROOT_DIR, 'data')
PLUGIN_LOWLEVEL_DIR = os.path.join(DATA_DIR, 'plugin_lowlevel')
LNAKO_DIR = os.path.join(DATA_DIR, 'lnako')
DB_PATH = os.path.join(DATA_DIR, 'nako3commands.db')

def load_catalog():
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

# ジャンル定義
GENRE_MAP = {
    27: 'ストリームIO',
    28: '標準入出力',
    29: 'ファイルシステム',
    31: 'ファイルメタデータ',
    32: 'ハッシュストリーム',
    33: 'ディレクトリ走査',
    34: '権限・属性管理',
    35: 'プロセス・端末制御',
    36: '高度ファイルシステム',
    37: '機能問い合わせ',
    38: '国際化・表示幅',
}

CMD_DETAILS = {
    # Issue 27
    'ファイル開く': {
        'desc': '指定したパスのファイルを開き、不透明なファイルハンドルオブジェクトを返します。MODEには文字列で読み書きモード（"r", "r+", "w", "w+", "a", "a+" やバイナリ修飾 "b" など）を指定できます。MODEを省略した場合は読み込み専用モードとなります。',
        'example': '''F = 「/tmp/test_open.txt」を「w+b」でファイル開く。
Fをファイル閉じる。
「/tmp/test_open.txt」をファイルリンク削除。
「ファイル開閉成功」と表示。
### lnako表示結果: ファイル開閉成功''',
        'refs': ['plugin_lowlevel/ファイル閉じる', 'plugin_lowlevel/ファイルバイト読む', 'plugin_lowlevel/ファイルバイト書く']
    },
    'ファイル閉じる': {
        'desc': '指定したファイルハンドルを閉じ、システムリソースを解放します。一度閉じたハンドルや無効なハンドルに対して操作を行うと、構造化エラーEBADFが発生します。',
        'example': '''F = 「/tmp/test_close.txt」を「w+b」でファイル開く。
Fをファイル閉じる。
「/tmp/test_close.txt」をファイルリンク削除。
「ファイルクローズ成功」と表示。
### lnako表示結果: ファイルクローズ成功''',
        'refs': ['plugin_lowlevel/ファイル開く']
    },
    'ファイルバイト読む': {
        'desc': 'ファイルハンドルから最大SIZEバイトのバイナリデータ（Bytes）を読み込みます。ファイルの終端（EOF）に達した場合は、長さ0の空のBytesを返します。',
        'example': '''H = 「sha256」でハッシュ開始。
B = Hをハッシュ完了。
F = 「/tmp/test_read.bin」を「w+b」でファイル開く。
FへBをファイルバイト書く。
Fをファイル閉じる。

F2 = 「/tmp/test_read.bin」を「rb」でファイル開く。
B2 = F2から32をファイルバイト読む。
F2をファイル閉じる。
「/tmp/test_read.bin」をファイルリンク削除。

H2 = 「sha256」でハッシュ開始。
H2へB2をハッシュ追加。
R = H2を「hex」でハッシュ完了。
Rを表示。
### lnako表示結果: 5df6e0e2761359d30a8275058e299fcc0381534545f55cf43e41983f5d4c9456''',
        'refs': ['plugin_lowlevel/ファイル開く', 'plugin_lowlevel/ファイルバイト書く', 'plugin_lowlevel/ファイル閉じる']
    },
    'ファイルバイト書く': {
        'desc': 'ファイルハンドルに対してバイナリデータ（Bytes）を書き込みます。実際に書き込まれたバイト数を返します。書き込むデータはBytes型である必要があります。',
        'example': '''H = 「sha256」でハッシュ開始。
B = Hをハッシュ完了。
F = 「/tmp/test_write.bin」を「w+b」でファイル開く。
N = FへBをファイルバイト書く。
Fをファイル閉じる。
「/tmp/test_write.bin」をファイルリンク削除。
Nを表示。
### lnako表示結果: 32''',
        'refs': ['plugin_lowlevel/ファイル開く', 'plugin_lowlevel/ファイルバイト読む', 'plugin_lowlevel/ファイル同期']
    },
    'ファイル同期': {
        'desc': 'ファイルハンドルの未書き込みバッファをストレージデバイスにフラッシュ（同期）します。POSIXのfsyncに相当します。',
        'example': '''H = 「sha256」でハッシュ開始。
B = Hをハッシュ完了。
F = 「/tmp/test_sync.bin」を「w+b」でファイル開く。
FへBをファイルバイト書く。
Fをファイル同期。
Fをファイル閉じる。
「/tmp/test_sync.bin」をファイルリンク削除。
「同期成功」と表示。
### lnako表示結果: 同期成功''',
        'refs': ['plugin_lowlevel/ファイル開く', 'plugin_lowlevel/ファイルバイト書く']
    },
    'ファイル切詰': {
        'desc': '開いているファイルハンドルのサイズを指定したバイト数SIZEに変更（切り詰め、または拡張）します。POSIXのftruncateに相当します。',
        'example': '''H = 「sha256」でハッシュ開始。
B = Hをハッシュ完了。
F = 「/tmp/test_trunc.bin」を「w+b」でファイル開く。
FへBをファイルバイト書く。
Fを16にファイル切詰。
Fをファイル閉じる。
INFO = 「/tmp/test_trunc.bin」をファイル詳細情報取得。
「/tmp/test_trunc.bin」をファイルリンク削除。
INFO[「size」]を表示。
### lnako表示結果: 16''',
        'refs': ['plugin_lowlevel/ファイル開く', 'plugin_lowlevel/ファイル詳細情報取得']
    },
    'ファイル位置変更': {
        'desc': '※この命令は現在策定中（未実装）です。ファイルハンドルのシーク位置を変更します（lseek相当）。WHENCEにはSEEK_SET/SEEK_CUR/SEEK_END相当の指定を行います。',
        'example': '''# 実装後のイメージ:
# Fを10でファイル位置変更。''',
        'refs': ['plugin_lowlevel/ファイル位置取得', 'plugin_lowlevel/ファイル開く']
    },
    'ファイル位置取得': {
        'desc': '※この命令は現在策定中（未実装）です。ファイルハンドルの現在のシーク位置（オフセット）を取得します。',
        'example': '''# 実装後のイメージ:
# POS = Fのファイル位置取得。''',
        'refs': ['plugin_lowlevel/ファイル位置変更']
    },
    'ファイル位置指定読込': {
        'desc': '※この命令は現在策定中（未実装）です。ファイルポインタの位置を変更せずに、指定オフセットからバイト列を読み込みます（pread相当）。',
        'example': '''# 実装後のイメージ:
# B = Fを0から100をファイル位置指定読込。''',
        'refs': ['plugin_lowlevel/ファイル位置指定書込', 'plugin_lowlevel/ファイルバイト読む']
    },
    'ファイル位置指定書込': {
        'desc': '※この命令は現在策定中（未実装）です。ファイルポインタの位置を変更せずに、指定オフセットへバイト列を書き込みます（pwrite相当）。',
        'example': '''# 実装後のイメージ:
# Fへ0にBYTESをファイル位置指定書込。''',
        'refs': ['plugin_lowlevel/ファイル位置指定読込', 'plugin_lowlevel/ファイルバイト書く']
    },

    # Issue 28
    '標準入力バイト読む': {
        'desc': '標準入力から最大SIZEバイトのバイナリデータ（Bytes）を直接読み込みます。EOFに達した場合は長さ0の空のBytesを返します。テキスト系の入力命令と内部の入力バッファ状態を共有します。\\n\\n対話的な標準入力が必要なため、DocTestでは実行結果を検証していません。',
        'example': '''# 5バイト読み取る例:
B = 5で標準入力バイト読む。''',
        'refs': ['plugin_lowlevel/標準出力バイト書く', 'plugin_lowlevel/標準エラー出力バイト書く']
    },
    '標準出力バイト書く': {
        'desc': '標準出力へバイナリデータ（Bytes）を直接書き込みます。改行文字の自動付与や文字コード変換は行われません。実際に書き込まれたバイト数を返します。\\n\\n生バイナリを出力するため、DocTestでは実行結果を検証していません。',
        'example': '''H = 「sha256」でハッシュ開始。
B = Hをハッシュ完了。
Bで標準出力バイト書く。''',
        'refs': ['plugin_lowlevel/標準出力同期', 'plugin_lowlevel/標準エラー出力バイト書く']
    },
    '標準エラー出力バイト書く': {
        'desc': '標準エラー出力へバイナリデータ（Bytes）を直接書き込みます。実際に書き込まれたバイト数を返します。\\n\\n生バイナリを出力するため、DocTestでは実行結果を検証していません。',
        'example': '''H = 「sha256」でハッシュ開始。
B = Hをハッシュ完了。
Bで標準エラー出力バイト書く。''',
        'refs': ['plugin_lowlevel/標準エラー出力同期', 'plugin_lowlevel/標準出力バイト書く']
    },
    '標準出力同期': {
        'desc': '標準出力のバッファを同期（フラッシュ）します。\\n\\n端末やパイプ環境ではOSの制限によりエラーになる場合があるため、DocTestでは実行結果を検証していません。',
        'example': '''標準出力同期。''',
        'refs': ['plugin_lowlevel/標準出力バイト書く', 'plugin_lowlevel/標準エラー出力同期']
    },
    '標準エラー出力同期': {
        'desc': '標準エラー出力のバッファを同期（フラッシュ）します。\\n\\n端末やパイプ環境ではOSの制限によりエラーになる場合があるため、DocTestでは実行結果を検証していません。',
        'example': '''標準エラー出力同期。''',
        'refs': ['plugin_lowlevel/標準エラー出力バイト書く', 'plugin_lowlevel/標準出力同期']
    },

    # Issue 29
    'ファイル詳細情報取得': {
        'desc': '指定パスのファイルやディレクトリの詳細情報（stat）を取得し、辞書形式で返します。辞書には種別kind（"file", "directory", "symlink"など）、サイズsize、権限mode、所有者uid/gid、リンク数nlink、タイムスタンプ（atimeNs, mtimeNs, ctimeNs, birthtimeNs: ナノ秒BigInt）などが含まれます。シンボリックリンクの場合はリンク先を追跡した実体の情報を返します。',
        'example': '''F = 「/tmp/test_stat.bin」を「w+b」でファイル開く。
Fをファイル閉じる。
INFO = 「/tmp/test_stat.bin」をファイル詳細情報取得。
「/tmp/test_stat.bin」をファイルリンク削除。
INFO[「kind」]を表示。
### lnako表示結果: file''',
        'refs': ['plugin_lowlevel/シンボリックリンク情報取得', 'plugin_lowlevel/実体パス取得']
    },
    'シンボリックリンク情報取得': {
        'desc': '指定パスのシンボリックリンク自体の詳細情報（lstat）を取得し、辞書形式で返します。ファイル詳細情報取得（stat）とは異なり、シンボリックリンク自体を追跡せず、リンクそのものの属性情報を返します。',
        'example': '''F = 「/tmp/test_lstat_src.txt」を「w+b」でファイル開く。
Fをファイル閉じる。
「/tmp/test_lstat_src.txt」を「/tmp/test_lstat_link.txt」へシンボリックリンク作成。
LINFO = 「/tmp/test_lstat_link.txt」のシンボリックリンク情報取得。
「/tmp/test_lstat_link.txt」をファイルリンク削除。
「/tmp/test_lstat_src.txt」をファイルリンク削除。
LINFO[「kind」]を表示。
### lnako表示結果: symlink''',
        'refs': ['plugin_lowlevel/ファイル詳細情報取得', 'plugin_lowlevel/シンボリックリンク作成']
    },
    'シンボリックリンク作成': {
        'desc': 'TARGETを指すシンボリックリンクをLINKのパスに作成します。POSIXのsymlinkに相当します。',
        'example': '''F = 「/tmp/test_sym_src.txt」を「w+b」でファイル開く。
Fをファイル閉じる。
「/tmp/test_sym_src.txt」を「/tmp/test_sym_link.txt」へシンボリックリンク作成。
LINFO = 「/tmp/test_sym_link.txt」のシンボリックリンク情報取得。
「/tmp/test_sym_link.txt」をファイルリンク削除。
「/tmp/test_sym_src.txt」をファイルリンク削除。
LINFO[「kind」]を表示。
### lnako表示結果: symlink''',
        'refs': ['plugin_lowlevel/シンボリックリンク先取得', 'plugin_lowlevel/ハードリンク作成']
    },
    'シンボリックリンク先取得': {
        'desc': '指定したシンボリックリンクが指している参照先のパス文字列を取得します。POSIXのreadlinkに相当します。',
        'example': '''F = 「/tmp/test_rlink_src.txt」を「w+b」でファイル開く。
Fをファイル閉じる。
「/tmp/test_rlink_src.txt」を「/tmp/test_rlink_link.txt」へシンボリックリンク作成。
TARGET = 「/tmp/test_rlink_link.txt」のシンボリックリンク先取得。
「/tmp/test_rlink_link.txt」をファイルリンク削除。
「/tmp/test_rlink_src.txt」をファイルリンク削除。
TARGETを表示。
### lnako表示結果: /tmp/test_rlink_src.txt''',
        'refs': ['plugin_lowlevel/シンボリックリンク作成', 'plugin_lowlevel/実体パス取得']
    },
    'ハードリンク作成': {
        'desc': 'TARGETに対する新しいハードリンクをLINKのパスに作成します。POSIXのlinkに相当します。同一ファイルシステムの既存ファイルに対してのみ作成できます。',
        'example': '''F = 「/tmp/test_hard_src.txt」を「w+b」でファイル開く。
Fをファイル閉じる。
「/tmp/test_hard_src.txt」を「/tmp/test_hard_link.txt」へハードリンク作成。
INFO = 「/tmp/test_hard_link.txt」のファイル詳細情報取得。
「/tmp/test_hard_link.txt」をファイルリンク削除。
「/tmp/test_hard_src.txt」をファイルリンク削除。
INFO[「nlink」]を表示。
### lnako表示結果: 2''',
        'refs': ['plugin_lowlevel/シンボリックリンク作成', 'plugin_lowlevel/ファイルリンク削除']
    },
    '実体パス取得': {
        'desc': '指定パスに含まれるシンボリックリンクや相対参照（.や..）をすべて解決した、正規の絶対パス（実体パス）文字列を取得します。POSIXのrealpathに相当します。',
        'example': '''F = 「/tmp/test_real_src.txt」を「w+b」でファイル開く。
Fをファイル閉じる。
「/tmp/test_real_src.txt」を「/tmp/test_real_link.txt」へシンボリックリンク作成。
REAL = 「/tmp/test_real_link.txt」の実体パス取得。
「/tmp/test_real_link.txt」をファイルリンク削除。
「/tmp/test_real_src.txt」をファイルリンク削除。
FNAME = REALからファイル名抽出。
FNAMEを表示。
### lnako表示結果: test_real_src.txt''',
        'refs': ['plugin_lowlevel/シンボリックリンク先取得', 'plugin_lowlevel/ファイル詳細情報取得']
    },
    'パス名変更': {
        'desc': 'ファイルまたはディレクトリのパス名を変更（移動）します。POSIXのrenameに相当します。',
        'example': '''F = 「/tmp/test_ren_old.txt」を「w+b」でファイル開く。
Fをファイル閉じる。
「/tmp/test_ren_old.txt」を「/tmp/test_ren_new.txt」へパス名変更。
INFO = 「/tmp/test_ren_new.txt」のファイル詳細情報取得。
「/tmp/test_ren_new.txt」をファイルリンク削除。
INFO[「kind」]を表示。
### lnako表示結果: file''',
        'refs': ['plugin_lowlevel/ファイルリンク削除', 'plugin_lowlevel/空フォルダ削除']
    },
    'ファイルリンク削除': {
        'desc': '指定パスのファイルリンク（ディレクトリエントリ）を削除します。ハードリンク数が0になるとストレージ上の実体領域が解放されます。POSIXのunlinkに相当します。ディレクトリに対して実行した場合はEISDIRエラーになります。',
        'example': '''F = 「/tmp/test_unlink.txt」を「w+b」でファイル開く。
Fをファイル閉じる。
「/tmp/test_unlink.txt」をファイルリンク削除。
「削除成功」と表示。
### lnako表示結果: 削除成功''',
        'refs': ['plugin_lowlevel/空フォルダ削除', 'plugin_lowlevel/ファイル開く']
    },
    '空フォルダ削除': {
        'desc': '指定された空のディレクトリを削除します。POSIXのrmdirに相当します。ファイルが存在するディレクトリに対して実行するとENOTEMPTYエラーになり、通常ファイルに対して実行するとENOTDIRエラーになります。',
        'example': '''「/tmp/test_rmdir_dir」のフォルダ作成。
「/tmp/test_rmdir_dir」を空フォルダ削除。
「フォルダ削除成功」と表示。
### lnako表示結果: フォルダ削除成功''',
        'refs': ['plugin_lowlevel/ファイルリンク削除']
    },

    # Issue 31
    'ファイルサイズ変更': {
        'desc': 'パス指定でファイルのサイズを指定したバイト数SIZEに変更（切り詰め・拡張）します。POSIXのtruncateに相当します。ファイルハンドルを開かずに直接ファイルサイズを変更できます。',
        'example': '''H = 「sha256」でハッシュ開始。
B = Hをハッシュ完了。
F = 「/tmp/test_truncate.bin」を「w+b」でファイル開く。
FへBをファイルバイト書く。
Fをファイル閉じる。
「/tmp/test_truncate.bin」を8にファイルサイズ変更。
INFO = 「/tmp/test_truncate.bin」のファイル詳細情報取得。
「/tmp/test_truncate.bin」をファイルリンク削除。
INFO[「size」]を表示。
### lnako表示結果: 8''',
        'refs': ['plugin_lowlevel/ファイル切詰', 'plugin_lowlevel/ファイル詳細情報取得']
    },
    'ファイル時刻設定': {
        'desc': 'パス指定でファイルのアクセス日時（ATIME）と更新日時（MTIME）を設定します。ナノ秒単位の整数値（またはBigInt）を指定します。POSIXのutimensat/utimeに相当します。',
        'example': '''F = 「/tmp/test_utime.txt」を「w+b」でファイル開く。
Fをファイル閉じる。
「/tmp/test_utime.txt」を1000000000から2000000000までファイル時刻設定。
INFO = 「/tmp/test_utime.txt」のファイル詳細情報取得。
「/tmp/test_utime.txt」をファイルリンク削除。
もし、(INFO[「mtimeNs」] == 2000000000)ならば
　　「時刻設定成功」と表示。
ここまで
### lnako表示結果: 時刻設定成功''',
        'refs': ['plugin_lowlevel/ファイル時刻設定済', 'plugin_lowlevel/ファイル詳細情報取得']
    },
    'ファイル時刻設定済': {
        'desc': '開いているファイルハンドルに対してアクセス日時（ATIME）と更新日時（MTIME）を設定します。POSIXのfutimensに相当します。',
        'example': '''F = 「/tmp/test_futime.txt」を「w+b」でファイル開く。
Fを1000000000から2000000000までファイル時刻設定済。
Fをファイル閉じる。
INFO = 「/tmp/test_futime.txt」のファイル詳細情報取得。
「/tmp/test_futime.txt」をファイルリンク削除。
もし、(INFO[「mtimeNs」] == 2000000000)ならば
　　「時刻設定済成功」と表示。
ここまで
### lnako表示結果: 時刻設定済成功''',
        'refs': ['plugin_lowlevel/ファイル時刻設定', 'plugin_lowlevel/ファイル開く']
    },

    # Issue 32
    'ハッシュ開始': {
        'desc': '指定したアルゴリズム（"sha256", "sha512", "sha1", "md5"など）による逐次ハッシュ計算を開始し、不透明なハッシュハンドルオブジェクトを返します。',
        'example': '''H = 「sha256」でハッシュ開始。
B = Hをハッシュ完了。
「ハッシュ開始成功」と表示。
### lnako表示結果: ハッシュ開始成功''',
        'refs': ['plugin_lowlevel/ハッシュ追加', 'plugin_lowlevel/ハッシュ完了', 'plugin_lowlevel/ハッシュ破棄']
    },
    'ハッシュ追加': {
        'desc': 'ハッシュ計算ハンドルにバイナリデータ（Bytes）をチャンクとして逐次追加します。大きなファイルやストリームデータをメモリに一括ロードせずに分割ハッシュ計算できます。',
        'example': '''H1 = 「sha256」でハッシュ開始。
B = H1をハッシュ完了。
H2 = 「sha256」でハッシュ開始。
H2へBをハッシュ追加。
R = H2を「hex」でハッシュ完了。
Rを表示。
### lnako表示結果: 5df6e0e2761359d30a8275058e299fcc0381534545f55cf43e41983f5d4c9456''',
        'refs': ['plugin_lowlevel/ハッシュ開始', 'plugin_lowlevel/ハッシュ完了', 'plugin_lowlevel/ハッシュ破棄']
    },
    'ハッシュ完了': {
        'desc': 'ハッシュ計算を終了し、計算結果（ダイジェスト）を取得します。ENCODINGに"hex"や"base64"を指定すると文字列で返し、ENCODINGを省略した場合はバイナリデータ（Bytes）として返します。完了後のハンドルは自動的に無効化され、再利用はEBADFエラーになります。',
        'example': '''H = 「sha256」でハッシュ開始。
R = Hを「hex」でハッシュ完了。
Rを表示。
### lnako表示結果: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855''',
        'refs': ['plugin_lowlevel/ハッシュ開始', 'plugin_lowlevel/ハッシュ追加', 'plugin_lowlevel/ハッシュ破棄']
    },
    'ハッシュ破棄': {
        'desc': '進行中のハッシュ計算を途中で破棄し、関連するメモリやリソースを解放します。二重破棄や無効ハンドルの破棄はEBADFエラーになります。',
        'example': '''H = 「sha256」でハッシュ開始。
Hをハッシュ破棄。
「ハッシュ破棄成功」と表示。
### lnako表示結果: ハッシュ破棄成功''',
        'refs': ['plugin_lowlevel/ハッシュ開始', 'plugin_lowlevel/ハッシュ完了']
    },

    # Issue 33
    'ディレクトリ開く': {
        'desc': '指定パスのディレクトリを開き、逐次走査用のディレクトリハンドルを返します。POSIXのopendirに相当します。',
        'example': '''DH = 「/tmp」をディレクトリ開く。
ENT = DHのディレクトリ次取得。
DHをディレクトリ閉じる。
もし、(ENT != 空)ならば
　　「ディレクトリ走査成功」と表示。
ここまで
### lnako表示結果: ディレクトリ走査成功''',
        'refs': ['plugin_lowlevel/ディレクトリ次取得', 'plugin_lowlevel/ディレクトリ閉じる', 'plugin_lowlevel/ディレクトリ列挙時']
    },
    'ディレクトリ次取得': {
        'desc': 'ディレクトリハンドルから次のエントリ情報を取得し、名前nameと種別type（"file", "directory", "symlink"など）を持つ辞書を返します。POSIXのreaddirに相当します。最後のエントリに達するとnullを返します。エントリ一覧には"."や".."は含まれません。',
        'example': '''DH = 「/tmp」をディレクトリ開く。
ENT = DHのディレクトリ次取得。
DHをディレクトリ閉じる。
もし、(ENT[「name」] != 「」)ならば
　　「エントリ取得成功」と表示。
ここまで
### lnako表示結果: エントリ取得成功''',
        'refs': ['plugin_lowlevel/ディレクトリ開く', 'plugin_lowlevel/ディレクトリ閉じる']
    },
    'ディレクトリ閉じる': {
        'desc': 'ディレクトリハンドルを閉じ、走査リソースを解放します。POSIXのclosedirに相当します。',
        'example': '''DH = 「/tmp」をディレクトリ開く。
DHをディレクトリ閉じる。
「ディレクトリクローズ成功」と表示。
### lnako表示結果: ディレクトリクローズ成功''',
        'refs': ['plugin_lowlevel/ディレクトリ開く']
    },
    'ディレクトリ列挙時': {
        'desc': '指定ディレクトリ内のエントリを1件ずつコールバック関数に渡して反復実行します。コールバック関数にはエントリ辞書ENT（name, type）が引数として渡されます。',
        'example': '''CNT = 0
●(ENTで)カウントCB
　　CNT = CNT + 1
ここまで
「/tmp」を「カウントCB」でディレクトリ列挙時。
もし、(CNT > 0)ならば
　　「ディレクトリ列挙成功」と表示。
ここまで
### lnako表示結果: ディレクトリ列挙成功''',
        'refs': ['plugin_lowlevel/ディレクトリ開く', 'plugin_lowlevel/ディレクトリ次取得']
    },

    # Issue 34
    'ファイル権限設定': {
        'desc': '指定パスのファイルのアクセス権限（パーミッション）を数値MODE（例: 0o644, 0o755）で設定します。POSIXのchmodに相当します。',
        'example': '''F = 「/tmp/test_chmod.txt」を「w+b」でファイル開く。
Fをファイル閉じる。
「/tmp/test_chmod.txt」を0o644でファイル権限設定。
「/tmp/test_chmod.txt」をファイルリンク削除。
「権限設定成功」と表示。
### lnako表示結果: 権限設定成功''',
        'refs': ['plugin_lowlevel/ファイル所有者設定', 'plugin_lowlevel/ファイルアクセス可能']
    },
    'ファイル所有者設定': {
        'desc': '指定パスのファイルの所有者UIDおよび所属グループGIDを設定します。POSIXのchownに相当します。変更しないIDには-1を指定します。\\n\\n※管理者権限が必要な操作のため、DocTestでは特定値の検証を行っていません。',
        'example': '''# 「data.txt」を所有者1000、グループ1000に設定する例:
「data.txt」を1000と1000でファイル所有者設定。''',
        'refs': ['plugin_lowlevel/シンボリックリンク所有者設定', 'plugin_lowlevel/ファイル権限設定']
    },
    'シンボリックリンク所有者設定': {
        'desc': 'シンボリックリンク自体の所有者UIDおよび所属グループGIDを設定します。リンク先を追跡しません。POSIXのlchownに相当します。\\n\\n※管理者権限が必要な操作のため、DocTestでは特定値の検証を行っていません。',
        'example': '''# 「link.txt」のシンボリックリンク自体の所有者を変更する例:
「link.txt」を1000と1000でシンボリックリンク所有者設定。''',
        'refs': ['plugin_lowlevel/ファイル所有者設定']
    },
    'ファイルアクセス可能': {
        'desc': '現在のプロセスが指定パスのファイルに対して指定されたアクセス権限MODE（読み取り: 4, 書き込み: 2, 実行: 1, 存在確認: 0）を持つかを判定します。POSIXのaccessに相当します。アクセス可能ならtrue、不可ならfalseを返します。',
        'example': '''F = 「/tmp/test_access.txt」を「w+b」でファイル開く。
Fをファイル閉じる。
「/tmp/test_access.txt」を4でファイルアクセス可能。
それを表示。
「/tmp/test_access.txt」をファイルリンク削除。
### lnako表示結果: true''',
        'refs': ['plugin_lowlevel/ファイル権限設定', 'plugin_lowlevel/ファイル詳細情報取得']
    },
    'UID取得': {
        'desc': '現在のプロセスの実ユーザーID（UID）を数値で取得します。POSIXのgetuidに相当します。',
        'example': '''UID取得。
U = それ。
もし、(U >= 0)ならば
　　「UID取得成功」と表示。
ここまで
### lnako表示結果: UID取得成功''',
        'refs': ['plugin_lowlevel/EUID取得', 'plugin_lowlevel/GID取得']
    },
    'EUID取得': {
        'desc': '現在のプロセスの実効ユーザーID（EUID）を数値で取得します。POSIXのgeteuidに相当します。',
        'example': '''EUID取得。
U = それ。
もし、(U >= 0)ならば
　　「EUID取得成功」と表示。
ここまで
### lnako表示結果: EUID取得成功''',
        'refs': ['plugin_lowlevel/UID取得']
    },
    'GID取得': {
        'desc': '現在のプロセスの実グループID（GID）を数値で取得します。POSIXのgetgidに相当します。',
        'example': '''GID取得。
G = それ。
もし、(G >= 0)ならば
　　「GID取得成功」と表示。
ここまで
### lnako表示結果: GID取得成功''',
        'refs': ['plugin_lowlevel/EGID取得', 'plugin_lowlevel/UID取得']
    },
    'EGID取得': {
        'desc': '現在のプロセスの実効グループID（EGID）を数値で取得します。POSIXのgetegidに相当します。',
        'example': '''EGID取得。
G = それ。
もし、(G >= 0)ならば
　　「EGID取得成功」と表示。
ここまで
### lnako表示結果: EGID取得成功''',
        'refs': ['plugin_lowlevel/GID取得']
    },
    '所属グループID一覧取得': {
        'desc': '現在のプロセスが所属している補助グループIDの一覧を数値配列で取得します。POSIXのgetgroupsに相当します。',
        'example': '''所属グループID一覧取得。
L = それ。
もし、(Lの要素数 >= 0)ならば
　　「グループ取得成功」と表示。
ここまで
### lnako表示結果: グループ取得成功''',
        'refs': ['plugin_lowlevel/GID取得']
    },
    'UMASK変更': {
        'desc': 'プロセスのファイル作成マスク（umask）を指定したMODEに変更し、変更前の旧マスク値を数値で返します。POSIXのumaskに相当します。',
        'example': '''0o022でUMASK変更。
OLD = それ。
OLDでUMASK変更。
「UMASK設定成功」と表示。
### lnako表示結果: UMASK設定成功''',
        'refs': ['plugin_lowlevel/ファイル権限設定']
    },

    # Issue 35
    'プロセス起動': {
        'desc': 'シェルを介さず引数配列ARGVを直接指定して外部プロセスを安全に起動し、プロセスハンドルを返します。POSIXのposix_spawnp/execに相当します。OPTIONSには作業ディレクトリcwdや環境変数envなどを指定できます。',
        'example': '''PROC = [「true」]をプロセス起動。
RES = PROCのプロセス待機。
もし、(RES[「exitCode」] == 0)ならば
　　「プロセス実行成功」と表示。
ここまで
### lnako表示結果: プロセス実行成功''',
        'refs': ['plugin_lowlevel/プロセス待機', 'plugin_lowlevel/シグナル送信']
    },
    'プロセス待機': {
        'desc': '起動した子プロセスの終了を待機し、終了ステータスコードexitCodeや受信シグナルsignalを含む辞書を返します。POSIXのwaitpidに相当します。',
        'example': '''PROC = [「true」]をプロセス起動。
RES = PROCのプロセス待機。
RES[「exitCode」]を表示。
### lnako表示結果: 0''',
        'refs': ['plugin_lowlevel/プロセス起動']
    },
    'プロセスID取得': {
        'desc': '自プロセスのプロセスID（PID）を取得します。POSIXのgetpidに相当します。',
        'example': '''プロセスID取得。
PID = それ。
もし、(PID > 0)ならば
　　「プロセスID取得成功」と表示。
ここまで
### lnako表示結果: プロセスID取得成功''',
        'refs': ['plugin_lowlevel/親プロセスID取得']
    },
    '親プロセスID取得': {
        'desc': '親プロセスのプロセスID（PPID）を取得します。POSIXのgetppidに相当します。',
        'example': '''親プロセスID取得。
PPID = それ。
もし、(PPID > 0)ならば
　　「親プロセスID取得成功」と表示。
ここまで
### lnako表示結果: 親プロセスID取得成功''',
        'refs': ['plugin_lowlevel/プロセスID取得']
    },
    'シグナル送信': {
        'desc': '指定したPIDのプロセスに対してPOSIXシグナル番号SIGNAL（SIGTERM: 15, SIGINT: 2など）を送信します。POSIXのkillに相当します。',
        'example': '''# 自プロセスへシグナル0（生存確認）を送信する例:
プロセスID取得。
PID = それ。
PIDに0をシグナル送信。
「シグナル送信成功」と表示。
### lnako表示結果: シグナル送信成功''',
        'refs': ['plugin_lowlevel/プロセス起動', 'plugin_lowlevel/プロセスID取得']
    },
    'プロセス優先度取得': {
        'desc': '指定したPIDのプロセスの実行優先度（niceness値）を取得します。PIDに0を指定した場合は自プロセスが対象になります。POSIXのgetpriorityに相当します。',
        'example': '''0のプロセス優先度取得。
PRIO = それ。
もし、(PRIO >= -20 かつ PRIO <= 20)ならば
　　「優先度取得成功」と表示。
ここまで
### lnako表示結果: 優先度取得成功''',
        'refs': ['plugin_lowlevel/プロセス優先度設定']
    },
    'プロセス優先度設定': {
        'desc': '指定したPIDのプロセスの実行優先度（niceness値）を設定します。PIDに0を指定した場合は自プロセスが対象になります。POSIXのsetpriorityに相当します。優先度を下げる（値を大きくする）操作は一般ユーザーでも可能ですが、優先度を上げる（値を小さくする）操作には管理者権限が必要です。\\n\\n※権限やOS制約があるため、DocTestでは特定値の検証を行っていません。',
        'example': '''# 自プロセスの優先度を現在の値のまま再設定する例:
0のプロセス優先度取得。
PRIO = それ。
0をPRIOにプロセス優先度設定。''',
        'refs': ['plugin_lowlevel/プロセス優先度取得']
    },
    '端末判定': {
        'desc': '指定したストリームSTREAM（"stdin", "stdout", "stderr"）が端末（TTY）に接続されているかを判定します。POSIXのisattyに相当します。',
        'example': '''「stdin」を端末判定。
R = それ。
もし、(R == true または R == false)ならば
　　「端末判定成功」と表示。
ここまで
### lnako表示結果: 端末判定成功''',
        'refs': ['plugin_lowlevel/端末サイズ取得']
    },
    '端末サイズ取得': {
        'desc': '指定したストリームSTREAMが接続されている端末画面の行数rowsと列数columnsを持つ辞書を取得します。ioctl TIOCGWINSZに相当します。\\n\\n※端末（TTY）接続時のみ有効なため、DocTestでは実行結果を検証していません。',
        'example': '''# 端末サイズを取得する例:
「stdout」を端末サイズ取得。
SIZE = それ。''',
        'refs': ['plugin_lowlevel/端末判定']
    },

    # Issue 36
    'ファイルシステム情報取得': {
        'desc': '指定パスのファイルシステム情報（ブロックサイズblockSize、総ブロック数blocks、空きブロック数free、利用可能ブロック数available、ファイルノード数filesなど）を辞書形式で取得します。POSIXのstatvfs/statfsに相当します。',
        'example': '''FS = 「/tmp」のファイルシステム情報取得。
もし、(FS[「blockSize」] > 0)ならば
　　「FS情報取得成功」と表示。
ここまで
### lnako表示結果: FS情報取得成功''',
        'refs': ['plugin_lowlevel/ファイル詳細情報取得']
    },
    'ファイルクローン': {
        'desc': 'Copy-on-Write（CoW/reflink）機能を利用して、SRCからDSTへ高速・省容量でファイルをクローン（複製）します。APFSやBtrfsなどのCoW対応ファイルシステムで有効です。非対応環境ではENOTSUPエラーになります。',
        'example': '''# クローン対応環境での例:
「stream_file_io」を低レイヤー機能対応判定。
F = 「/tmp/test_clone_src.bin」を「w+b」でファイル開く。
Fをファイル閉じる。
「reflink」を低レイヤー機能対応判定。
もし、それがtrueならば
　　「/tmp/test_clone_src.bin」を「/tmp/test_clone_dst.bin」にファイルクローン。
　　「/tmp/test_clone_dst.bin」をファイルリンク削除。
ここまで
「/tmp/test_clone_src.bin」をファイルリンク削除。
「クローン処理完了」と表示。
### lnako表示結果: クローン処理完了''',
        'refs': ['plugin_lowlevel/ファイル領域確保']
    },
    'ファイルデータ領域検索': {
        'desc': 'スパースファイルにおいて、指定オフセットOFFSET以降でデータが存在する次の位置（SEEK_DATA）を検索し、そのオフセットを返します。',
        'example': '''F = 「/tmp/test_seek_data.bin」を「w+b」でファイル開く。
Fを0に1024でファイル領域確保。
Fを0からファイルデータ領域検索。
POS = それ。
Fをファイル閉じる。
「/tmp/test_seek_data.bin」をファイルリンク削除。
もし、(POS >= 0)ならば
　　「データ領域検索成功」と表示。
ここまで
### lnako表示結果: データ領域検索成功''',
        'refs': ['plugin_lowlevel/ファイル空洞領域検索', 'plugin_lowlevel/ファイル領域確保']
    },
    'ファイル空洞領域検索': {
        'desc': 'スパースファイルにおいて、指定オフセットOFFSET以降でホール（空洞領域 SEEK_HOLE）が存在する次の位置を検索し、そのオフセットを返します。',
        'example': '''F = 「/tmp/test_seek_hole.bin」を「w+b」でファイル開く。
Fを0に1024でファイル領域確保。
Fを0からファイル空洞領域検索。
POS = それ。
Fをファイル閉じる。
「/tmp/test_seek_hole.bin」をファイルリンク削除。
もし、(POS >= 0)ならば
　　「空洞領域検索成功」と表示。
ここまで
### lnako表示結果: 空洞領域検索成功''',
        'refs': ['plugin_lowlevel/ファイルデータ領域検索']
    },
    'ファイル領域確保': {
        'desc': 'ファイルハンドルに対して指定オフセットOFFSETから指定サイズSIZEの物理ディスク領域を事前に割り当て（事前確保）します。POSIXのfallocate/posix_fallocateに相当します。',
        'example': '''F = 「/tmp/test_falloc.bin」を「w+b」でファイル開く。
Fを0に1024でファイル領域確保。
Fをファイル閉じる。
INFO = 「/tmp/test_falloc.bin」のファイル詳細情報取得。
「/tmp/test_falloc.bin」をファイルリンク削除。
もし、(INFO[「size」] >= 1024)ならば
　　「領域確保成功」と表示。
ここまで
### lnako表示結果: 領域確保成功''',
        'refs': ['plugin_lowlevel/ファイル切詰', 'plugin_lowlevel/ファイルデータ領域検索']
    },

    # Issue 37
    '低レイヤー機能対応判定': {
        'desc': '現在のlnakoランタイムおよび実行環境（OS/ファイルシステム）が、指定された低レイヤー機能（capability ID）に対応しているかを判定します。対応している場合はtrue、非対応または未知の機能名の場合はfalseを返します。',
        'example': '''「stream_file_io」を低レイヤー機能対応判定。
それを表示。
「unknown_cap」を低レイヤー機能対応判定。
それを表示。
### lnako表示結果: true
### false''',
        'refs': ['plugin_lowlevel/低レイヤー機能一覧取得']
    },
    '低レイヤー機能一覧取得': {
        'desc': 'lnakoランタイムで認識可能な低レイヤー機能（capability ID）の全一覧を文字列の配列で取得します。',
        'example': '''一覧 = 低レイヤー機能一覧取得。
N = 一覧の要素数。
もし、N > 0ならば
　　「機能一覧取得成功」と表示。
ここまで
### lnako表示結果: 機能一覧取得成功''',
        'refs': ['plugin_lowlevel/低レイヤー機能対応判定']
    },

    # Issue 38
    'ロケール文字列比較': {
        'desc': 'ロケールと言語規則（Unicode Collation）を考慮して文字列Aと文字列Bを比較照合します。A < Bならば負の整数、A = Bならば0、A > Bならば正の整数を返します。OPTIONSには照合感度や大文字小文字の扱いなどの照合オプションを指定できます。',
        'example': '''「apple」を「banana」とロケール文字列比較。
C = それ。
もし、(C < 0)ならば
　　「比較成功」と表示。
ここまで
### lnako表示結果: 比較成功''',
        'refs': ['plugin_lowlevel/文字表示幅取得']
    },
    '文字表示幅取得': {
        'desc': '文字列TEXTのターミナル・コンソール上での表示幅（半角文字換算のカラム数）を計算して返します。日本語の全角文字、半角カタカナ、絵文字、結合文字、制御文字などを考慮した正確な表示幅を算出します。',
        'example': '''「なでしこ3」の文字表示幅取得。
それを表示。
### lnako表示結果: 9''',
        'refs': ['plugin_lowlevel/ロケール文字列比較']
    },
}

def generate_docs():
    os.makedirs(PLUGIN_LOWLEVEL_DIR, exist_ok=True)
    os.makedirs(LNAKO_DIR, exist_ok=True)
    
    catalog = load_catalog()
    commands = catalog['commands']

    for cmd in commands:
        name = cmd['name']
        particles = cmd.get('particles', '')
        issue = cmd.get('issue', 27)
        genre = GENRE_MAP.get(issue, '低レイヤー')
        impl = cmd.get('implemented', False)
        returns = cmd.get('returns', 'void')
        cap = cmd.get('capability')
        errors = cmd.get('errors', [])
        
        detail = CMD_DETAILS.get(name, {})
        desc_text = detail.get('desc', f'{name}を実行します。')
        example_text = detail.get('example', '')
        refs = detail.get('refs', [])

        # 本文生成
        content_lines = []
        content_lines.append('▲説明')
        content_lines.append('')
        content_lines.append('※この命令は、PC向けネイティブ版なでしこ「[[lnako]]」専用の命令です。ブラウザ版（wnako）やNode.js版（cnako）では動作しません。')
        content_lines.append('')
        content_lines.append(desc_text)
        content_lines.append('')
        
        # 仕様詳細
        content_lines.append('●仕様')
        content_lines.append('- 対応環境: [[lnako]]専用 (Web/Node.js非対応)')
        content_lines.append(f'- プラグイン: [[plugin_lowlevel]]')
        content_lines.append(f'- 分類: {genre}')
        content_lines.append(f'- 助詞: {particles if particles else "なし（引数0）"}')
        content_lines.append(f'- 戻り値: {returns}')
        content_lines.append(f'- 実装状況: {"実装済み" if impl else "未実装（策定中・ENOTSUP）"}')
        if cap:
            content_lines.append(f'- 機能ID (capability): `{cap}`')
        if errors:
            content_lines.append(f'- 発生し得るエラー: {", ".join(errors)}')
        content_lines.append('')
        
        content_lines.append('▲利用例')
        content_lines.append('')
        content_lines.append('{{{#nako3')
        content_lines.append(example_text)
        content_lines.append('}}}')
        content_lines.append('')

        if refs:
            content_lines.append('▲参考')
            content_lines.append('')
            for ref in refs:
                content_lines.append(f'- [[{ref}]]')
            content_lines.append('')

        file_content = '\n'.join(content_lines)

        # 1. data/plugin_lowlevel/{name}.txt に書き出し
        target_path = os.path.join(PLUGIN_LOWLEVEL_DIR, f'{name}.txt')
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(file_content)

        # 2. data/lnako/{name}.txt に include ファイルを生成
        lnako_cmd_path = os.path.join(LNAKO_DIR, f'{name}.txt')
        with open(lnako_cmd_path, 'w', encoding='utf-8') as f:
            f.write(f'#include(plugin_lowlevel/{name})\n')

    print(f'Generated {len(commands)} command documents in {PLUGIN_LOWLEVEL_DIR} and {LNAKO_DIR}')

    # plugin_lowlevel.txt 生成
    plugin_page = '''■ plugin_lowlevel

plugin_lowlevelは、PC向けネイティブなでしこ「lnako」専用の低レイヤーAPIプラグインです。
バイナリストリームI/O、Raw標準入出力、ファイルシステム操作、逐次ハッシュ計算、POSIX権限・プロセス管理、ロケール比較・表示幅計算など、OSネイティブの高速かつ精密なシステムプログラミングを可能にします。

● 主な機能
- **ストリームI/O**: ハンドルベースのファイル開閉、バイト単位の読込・書込、同期、切詰
- **Raw標準入出力**: 改行や文字コード変換を挟まない生バイト単位の標準入力・出力・エラー出力
- **ファイルシステム**: stat/lstat詳細メタデータ取得、シンボリックリンク/ハードリンク操作、実体パス取得、リネーム、リンク削除、空フォルダ削除
- **ファイルメタデータ**: ファイルサイズ変更（truncate）、高精度ファイルアクセス/更新日時設定（utime/futimens）
- **ディレクトリ走査**: opendir/readdir/closedirによる省メモリ逐次走査、反復列挙
- **権限・属性管理**: chmod/chownによるパーミッション・所有者設定、access権限検査、UID/GID取得、umask変更
- **プロセス・端末制御**: argvによる外部プロセス起動・待機、PID/PPID取得、シグナル送信、優先度設定、TTY判定・端末サイズ取得
- **高度ファイルシステム**: ファイルシステム容量情報取得（statfs）、Copy-on-Write複製（reflink）、SEEK_DATA/SEEK_HOLE検索、ディスク領域事前確保（fallocate）
- **逐次ハッシュストリーム**: sha256/sha512などの大容量データをメモリ節約して段階的にハッシュ計算
- **機能問い合わせ**: 実行OS・環境ごとの低レイヤー機能対応判定と一覧取得
- **国際化・表示幅**: ロケール言語規則に基づく文字列比較（Collation）、端末半角換算の表示幅計算

● 命令一覧
詳しくは [[lnako/命令一覧]] を参照してください。
'''
    with open(os.path.join(DATA_DIR, 'plugin_lowlevel.txt'), 'w', encoding='utf-8') as f:
        f.write(plugin_page)
    print('Generated data/plugin_lowlevel.txt')

def update_lnako_command_list():
    catalog = load_catalog()
    commands = catalog['commands']
    impl_count = sum(1 for c in commands if c.get('implemented', False))
    total_lowlevel = len(commands)

    # 既存の data/lnako/命令一覧.txt から標準命令部分（plugin_system以降）を抽出
    cmd_list_file = os.path.join(LNAKO_DIR, '命令一覧.txt')
    with open(cmd_list_file, 'r', encoding='utf-8') as f:
        orig_content = f.read()

    # 「● 実装済み標準命令 (527件)」以降を取得
    std_marker = '● 実装済み標準命令 (527件)'
    if std_marker in orig_content:
        std_section = orig_content[orig_content.find(std_marker):]
    else:
        raise ValueError('Standard section marker not found in 命令一覧.txt')

    # 独自命令セクションをジャンル別に構築
    by_genre = {}
    for c in commands:
        issue = c.get('issue', 27)
        genre = GENRE_MAP.get(issue, '低レイヤー')
        by_genre.setdefault(genre, []).append(c)

    custom_lines = []
    custom_lines.append(f'■ lnako命令一覧')
    custom_lines.append('')
    custom_lines.append(f'lnako独自命令 {impl_count}件(未実装{total_lowlevel - impl_count}件、計{total_lowlevel}件) / 実装済み標準命令 527件')
    custom_lines.append('')
    custom_lines.append(f'● lnako独自命令 ({impl_count}件実装 / 全{total_lowlevel}件)')
    custom_lines.append('')
    custom_lines.append('▲ plugin_lowlevel (低レイヤーAPI)')
    custom_lines.append('')

    for genre, cmds in by_genre.items():
        custom_lines.append(f'▲ {genre}')
        for c in cmds:
            name = c['name']
            particles = c.get('particles', '')
            impl = c.get('implemented', False)
            status_tag = '' if impl else '【未実装】'
            part_str = f' {particles}' if particles else ''
            custom_lines.append(f'- [[{name}:plugin_lowlevel/{name}]]{part_str}{status_tag}')
        custom_lines.append('')

    new_content = '\n'.join(custom_lines) + '\n' + std_section

    with open(cmd_list_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'Updated {cmd_list_file}')

def update_db():
    """SQLite DB に plugin_lowlevel と全命令を登録"""
    catalog = load_catalog()
    commands = catalog['commands']

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # plugins テーブルに plugin_lowlevel を登録
    cur.execute('''
        INSERT OR REPLACE INTO plugins (name, desc, nakotype)
        VALUES (?, ?, ?)
    ''', ('plugin_lowlevel', 'lnako低レイヤーAPIプラグイン', '基本プラグイン,lnako'))

    # commands テーブルから既存の plugin_lowlevel を一旦削除
    cur.execute("DELETE FROM commands WHERE plugin='plugin_lowlevel'")

    # commands テーブルに追加
    for cmd in commands:
        name = cmd['name']
        issue = cmd.get('issue', 27)
        genre = GENRE_MAP.get(issue, '低レイヤー')
        particles = cmd.get('particles', '')
        impl = cmd.get('implemented', False)
        notes = cmd.get('notes', '')
        detail = CMD_DETAILS.get(name, {})
        desc = detail.get('desc', notes)
        if not impl:
            desc = '【未実装】' + desc
        pagename = f'plugin_lowlevel/{name}'

        cur.execute('''
            INSERT OR REPLACE INTO commands (pagename, plugin, genre, name, type, kana, args, desc, src_url, ctime, mtime)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (pagename, 'plugin_lowlevel', genre, name, '関数', name, particles, desc, 'https://github.com/soramikan/lnako', 1789700000, 1789700000))

    conn.commit()
    conn.close()
    print(f'Updated {DB_PATH} with plugin_lowlevel and {len(commands)} commands')

if __name__ == '__main__':
    generate_docs()
    update_lnako_command_list()
    update_db()
