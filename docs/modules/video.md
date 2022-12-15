# Module video.py

```python
from bilibili_api import video
```

视频相关操作。

?> 注意，同时存在 page_index 和 cid 的参数，两者至少提供一个。

## const dict VIDEO_QUALITIES

视频清晰度枚举

## const dict AUDIO_QUALITIES

音频音质枚举

## const dict VIDEO_CODECS

视频编码枚举

## class DanmakuOperatorType(Enum)

弹幕操作枚举

+ DELETE - 删除弹幕
+ PROTECT - 保护弹幕
+ UNPROTECT - 取消保护弹幕

## class Video

视频类，各种对视频的操作均在里面。

### Attributes

| name | type | description |
| ---- | ---- | ----------- |
| credential | Credential | 凭据 |

### Functions

#### def \_\_init\_\_()

| name       | type                 | description                           |
| ---------- | -------------------- | ------------------------------------- |
| bvid       | str, optional        | BV 号。bvid 和 aid 必须提供其中之一。 |
| aid        | int, optional        | AV 号。bvid 和 aid 必须提供其中之一。 |
| credential | Credential, optional | Credential 类。Defaults to None.      |

#### def set_bvid()

| name | type | description |
| ---- | ---- | ----------- |
| bvid | str  | BV 号。     |

设置 bvid。

**Returns:** None

#### def get_bvid()

获取 bvid。

**Returns:** str: bvid

#### def set_aid()

| name | type | description |
| ---- | ---- | ----------- |
| aid  | int  | AV 号。     |

设置 aid。

**Returns:** None

#### def get_aid()

获取 aid。

**Returns:** int: aid

#### async def get_info()

获取视频信息。

**Returns:** API 调用返回结果。

#### async def get_stat()

获取视频统计数据（播放量，点赞数等）。

**Returns:** API 调用返回结果。

#### async def get_tags()

获取视频标签。

**Returns:** API 调用返回结果。

#### async def get_chargers()

获取视频充电用户。

**Returns:** API 调用返回结果。

#### async def get_video_snapshot()

| name | type | description |
| - | - | - |
| cid | int | 分 P 序号 |
| json_index | bool | 是否需要json 数组截取时间表 |
| pvideo | bool | 是否只获取封面预览 |

获取视频快照信息。

Tip:返回的 url 均不带 http 前缀，且只获取封面预览返回的是未转义的 url

**Returns:** WebAPI 调用返回结果

#### async def get_pages()

获取分 P 信息。

**Returns:** API 调用返回结果。

#### async def get_cid()

| name | type | description |
| - | - | - |
| page_index | int | 分 P 序号 |

获取稿件 cid。

#### async def get_download_url()

| name       | type          | description                          |
| ---------- | ------------- | ------------------------------------ |
| page_index | int, optional | 分 P 号，从 0 开始。Defaults to None |
| cid        | int, optional | 分 P 的 ID。Defaults to None         |
| html5      | bool, optional | 是否以 html5 平台访问，这样子能直接在网页中播放，但是链接少。 |

获取视频下载信息。

**Returns:** API 调用返回结果。

#### async def get_related()

获取相关视频信息。

**Returns:** API 调用返回结果。

#### async def has_liked()

视频是否点赞过。

**Returns:** bool: 视频是否点赞过。

#### async def get_pay_coins()

获取视频已投币数量。

**Returns:** int: 视频已投币数量。

#### async def has_favoured()

是否已收藏。

**Returns:** bool: 视频是否已收藏。

#### async def get_media_list()

获取收藏夹列表信息，用于收藏操作，含各收藏夹对该视频的收藏状态。

**Returns:** API 调用返回结果。

#### async def get_danmaku_view():

| name       | type          | description                          |
| ---------- | ------------- | ------------------------------------ |
| page_index | int, optional | 分 P 号，从 0 开始。Defaults to None |
| cid        | int, optional | 分 P 的 ID。Defaults to None         |

获取弹幕设置、特殊弹幕、弹幕数量、弹幕分段等信息。

**Returns:** API 调用返回结果。

#### async def get_danmakus()

| name       | type                    | description                                               |
| ---------- | ----------------------- | --------------------------------------------------------- |
| page_index | int, optional           | 分 P 号，从 0 开始。Defaults to None                      |
| date       | datetime.Date, optional | 指定日期后为获取历史弹幕，精确到年月日。Defaults to None. |
| cid        | int, optional           | 分 P 的 ID。Defaults to None                              |

获取弹幕。

**Returns:** List[Danmaku]: Danmaku 类的列表。

#### async def get_danmaku_xml()

| name | type | description |
| ---- | ---- | ----------- |
| page_index | int, optional | 分 P 号，从 0 开始。 |

获取所有弹幕的 XML 源

**Returns** str: XML 源

#### async def get_history_danmaku_index()

| name       | type                    | description                                               |
| ---------- | ----------------------- | --------------------------------------------------------- |
| page_index | int, optional           | 分 P 号，从 0 开始。Defaults to None                      |
| date       | datetime.Date, optional | 指定日期后为获取历史弹幕，精确到年月日。Defaults to None. |
| cid        | int, optional           | 分 P 的 ID。Defaults to None                              |

获取特定月份存在历史弹幕的日期。

**Returns:** None | List[str]: 调用 API 返回的结果。不存在时为 None。

#### async def has_liked_danmakus()

| name       | type          | description                          |
| ---------- | ------------- | ------------------------------------ |
| page_index | int, optional | 分 P 号，从 0 开始。Defaults to None |
| ids        | List[int]     | 要查询的弹幕 ID 列表。               |
| cid        | int, optional | 分 P 的 ID。Defaults to None         |

是否已点赞弹幕。

**Returns:** API 调用返回结果。

#### async def send_danmaku()

| name       | type          | description                          |
| ---------- | ------------- | ------------------------------------ |
| page_index | int, optional | 分 P 号，从 0 开始。Defaults to None |
| danmaku    | Danmaku       | Danmaku 类。                         |
| cid        | int, optional | 分 P 的 ID。Defaults to None         |

发送弹幕。

**Returns:** API 调用返回结果。

#### async def like_danmaku()

| name       | type           | description                          |
| ---------- | -------------- | ------------------------------------ |
| page_index | int, optional  | 分 P 号，从 0 开始。Defaults to None |
| dmid       | int            | 弹幕 ID。                            |
| status     | bool, optional | 点赞状态。Defaults to True.          |
| cid        | int, optional  | 分 P 的 ID。Defaults to None         |

点赞弹幕。

#### async def operate_danmaku()

| name       | type                | description                          |
| ---------- | ------------------- | ------------------------------------ |
| page_index | int, optional       | 分 P 号，从 0 开始。Defaults to None |
| dmids      | List[int]           | 弹幕 ID 列表。                       |
| type_      | DanmakuOperatorType | 操作类型                             |
| cid        | int, optional       | 分 P 的 ID。Defaults to None         |

操作弹幕（如删除、保护等）。

**Returns:** API 调用返回结果。

#### async def get_danmaku_snapshot()

获取弹幕快照

**Returns:** API 调用返回结果。

#### async def recall_danmaku()

| name | type | description |
| - | - | - |
| page_index | int | 分 P 号 |
| dmid | int | 弹幕 id |
| cid | int | 分 P 编码 |

撤回弹幕

**Returns:** API 调用返回结果。

#### async def get_pbp()

| name | type | description |
| - | - | - |
| page_index | int | 分 P 号 |
| cid | int | 分 P 编码 |

获取高能进度条

**Returns**: 调用 API 所得的结果。

#### async def like()

| name   | type           | description                 |
| ------ | -------------- | --------------------------- |
| status | bool, optional | 点赞状态。Defaults to True. |

点赞视频。

**Returns:** API 调用返回结果。

#### async def pay_coin()

| name | type           | description                          |
| ---- | -------------- | ------------------------------------ |
| num  | int, optional  | 硬币数量，为 1 ~ 2 个。Defaults to 1 |
| like | bool, optional | 是否同时点赞。Defaults to False      |

投币。

**Returns:** API 调用返回结果。

#### async def add_tag()

| name | type | description |
| ---- | ---- | ----------- |
| name | str  | 标签名字。  |

添加标签。

**Returns:** API 调用返回结果。

#### async def delete_tag()

| name   | type | description |
| ------ | ---- | ----------- |
| tag_id | int  | 标签 ID。   |

删除标签。

**Returns:** API 调用返回结果。

#### async def subscribe_tag()

| name   | type | description |
| ------ | ---- | ----------- |
| tag_id | int  | 标签 ID。   |

关注标签。

**Returns:** API 调用返回结果。

#### async def unsubscribe_tag()

| name   | type | description |
| ------ | ---- | ----------- |
| tag_id | int  | 标签 ID。   |

取关标签。

**Returns:** API 调用返回结果。

#### async def set_favorite()

| name          | type                | description                         |
| ------------- | ------------------- | ----------------------------------- |
| add_media_ids | List[int], optional | 要添加到的收藏夹 ID. Defaults to [] |
| del_media_ids | List[int], optional | 要移出的收藏夹 ID. Defaults to []   |

设置视频收藏状况。

**Returns:** API 调用返回结果。

#### async def get_subtitle()

| name       | type | description  |
|------------|------|--------------|
| cid        | cid  | 分 P id. 必须参数 |

无需登陆, 获取视频播放信息Api中的字幕数据字段。

**Returns:** API 调用返回结果。

#### async def submit_subtitle()

| name       | type | description                                                |
|------------|------|------------------------------------------------------------|
| lan        | str  | 字幕语言代码，参考 http://www.lingoes.cn/zh/translator/langcode.htm |
| data       | dict | 字幕数据                                                       |
| submit     | bool | 是否提交，不提交为草稿                                                |
| sign       | bool | 是否署名                                                       |
| page_index | int  | 分 P 索引. Defaults to None.                                  |
| cid        | cid  | 分 P id. Defaults to None.                                  |

上传字幕

字幕数据 data 参考：

```json
{
  "font_size": "float: 字体大小，默认 0.4",
  "font_color": "str: 字体颜色，默认 \"#FFFFFF\"",
  "background_alpha": "float: 背景不透明度，默认 0.5",
  "background_color": "str: 背景颜色，默认 \"#9C27B0\"",
  "Stroke": "str: 描边，目前作用未知，默认为 \"none\"",
  "body": [
    {
      "from": "int: 字幕开始时间（秒）",
      "to": "int: 字幕结束时间（秒）",
      "location": "int: 字幕位置，默认为 2",
      "content": "str: 字幕内容"
    }
  ]
}
```

**Returns:** API 调用返回结果。

#### async def add_to_toview()

添加视频至稍后再看

**Returns:** API 调用返回结果。

#### async def delete_from_toview()

从稍后再看列表删除视频

**Returns:** API 调用返回结果。

---

## class VideoOnlineMonitor

视频在线人数实时监测。

**示例代码：**

```python
import asyncio
from bilibili_api import video

# 实例化
r = video.VideoOnlineMonitor("BV1Bf4y1Q7QP")


# 装饰器方法注册事件监听器
@r.on("ONLINE")
async def handler(data):
    print(data)


# 函数方法注册事件监听器
async def handler2(data):
    print(data)
    r.add_event_listener("ONLINE", handler2)


asyncio.get_event_loop().run_until_complete(r.connect())
```

**事件表：**

| name         | description    | callback                        |
| ------------ | -------------- | ------------------------------- |
| ONLINE       | 在线人数更新 | dict                            |
| DANMAKU      | 收到实时弹幕   | Danmaku                         |
| DISCONNECTED | 正常断开连接   | None                            |
| ERROR        | 发生错误       | aiohttp.ClientWebSocketResponse |
| CONNECTED    | 成功连接       | None                            |

### Sub classes

#### class Datapack

**Extends:** enum.Enum

数据包类型枚举。

+ CLIENT_VERIFY  : 客户端发送验证信息。
+ SERVER_VERIFY  : 服务端响应验证信息。
+ CLIENT_HEARTBEAT: 客户端发送心跳包。
+ SERVER_HEARTBEAT: 服务端响应心跳包。
+ DANMAKU: 实时弹幕更新。

### Functions

#### def \_\_init\_\_()

| name       | type                 | description                                    |
| ---------- | -------------------- | ---------------------------------------------- |
| bvid       | str, optional        | BVID                                           |
| aid        | int, optional        | AID                                            |
| page_index | int, optional        | 分 P 序号. Defaults to 0.                      |
| credential | Credential, optional | Credential 类. Defaults to None.               |
| debug      | bool, optional       | 调试模式，将输出更详细信息. Defaults to False. |

#### async def connect()

连接服务器。

**Returns:** None

#### async def disconnect()

断开服务器。

**Returns:** None
