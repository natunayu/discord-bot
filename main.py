import discord
import requests, tempfile, json
from discord.ext import commands
import asyncio


# インテントの生成
intents = discord.Intents.default()
intents.message_content = True


#クライアントを生成
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)


#読み上げ用女性リスト
ladys = ['M-rutochan', 'M-aichan', 'M-mikeneko', 'M-kyaorichin', 'M-mizuman', 'M-tametsugu', 'M-natunayu']

#VC内メンバーの一時保存
vc_temp_list = []


#TOKENの取得
def getKey():
    f = open('Key', 'r')
    data = f.readline()
    f.close()
    return data


#idを指定 戻り値int
#先頭にC-でチャンネル M-でメンバー
def getId(key):
    f = open('idList', 'r')
    while True:
        data = f.readline()
        if key in data:
            break
    data = int(data.replace('\n', '').replace(key + ':', ''))
    return data


# discordと接続した時
@client.event
async def on_ready():
    print(f'たこぼっとが起動しました。')

    channel = client.get_channel(getId("C-testbox"))
    if channel is not None:
        #await channel.send('-----たこぼっとを起動しました-----')
        pass
    else:
        print('チャンネルが見つかりませんでした')


# メッセージを受信した時
@client.event
async def on_message(message):
    # 自分のメッセージを無効
    if message.author == client.user:
        return

    #特定のメッセージに対して応答
    if message.content.startswith('たこさんこんにちは'):
        await message.channel.send('はいこんにちは')

    #ladysリスト内の人のチャットを読み上げ
    if message.author.id in apply_func_to_list(getId, ladys):
        host = "127.0.0.1"
        port = 50021

        params = (
            ("text", await text_arrangement(message.content)),
            ("speaker", 3) # 音声の種類をInt型で指定
        )

        response1 = requests.post(
            f"http://{host}:{port}/audio_query",
            params=params
        )

        response2 = requests.post(
            f"http://{host}:{port}/synthesis",
            headers={"Content-Type": "application/json"},
            params=params,
            data=json.dumps(response1.json())
        )

        #テンポラリーディレクトリにあるwavファイルを展開
        with tempfile.TemporaryDirectory() as tmp:
            with open(f"{tmp}/audi.wav", "wb") as f:
                f.write(response2.content)
                voice_client = discord.utils.get(client.voice_clients, guild=message.guild)

                if voice_client is None:
                    # ボイスチャンネルに接続されていない場合は何もしない
                    return

                #再生
                voice_client.play(discord.FFmpegPCMAudio(f"{tmp}/audi.wav"))
                while voice_client.is_playing():
                    await asyncio.sleep(1)


#メンバーがボイスチャンネルを更新した時
@client.event
async def on_voice_state_update(member, before, after):

    if member.id in apply_func_to_list(getId, ladys) and before.channel is None and after.channel is not None:
        channel = after.channel
        await channel.connect()

    if member.id in apply_func_to_list(getId, ladys) and not after.channel:
        await client.voice_clients[0].disconnect()


#リスト要素全てに関数を適用したリストを戻す
def apply_func_to_list(func, lst):
    return [func(x) for x in lst]


#テキストを整理 idをニックネームに置換
async def text_arrangement(text):
    if '@' in text:
        for i in range(len(text)):
            if text[i] == '@' and i+1 < len(text) and text[i+1].isdigit():
                m_id = text[i+1:i+19]
                print(m_id)
                text = text[:i] + '@' + await id_to_nickname(m_id) + text[i+19:]

                #再帰呼び出しでIDを修正
                text = await text_arrangement(text)
                break
    return text if len(text) > 0 else ''


#idをニックネームに変換
async def id_to_nickname(m_id):
    for guild in client.guilds:
        member = await guild.fetch_member(m_id)
        if member:
            nickname = member.nick
            if nickname is None:
                nickname = member.name
            return nickname


#
async def



#クライアントの実行
TOKEN = getKey()
client.run(TOKEN)

