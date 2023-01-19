"""
bilibili_api.interactive_video

互动视频相关操作
"""

# pylint: skip-file

from asyncio import CancelledError, create_task
import copy
import enum
import json
import os
import shutil
import time
from typing import Callable, List, Tuple, Union
from .utils.Credential import Credential
from .utils.utils import get_api
from .utils.network_httpx import request
from .video import Video
from urllib import parse
from random import randint as rand
import requests
from . import settings
import zipfile
from .utils.AsyncEvent import AsyncEvent
from typing import Coroutine

API = get_api("interactive_video")


class InteractiveButtonAlign(enum.Enum):
    """
    按钮的文字在按钮中的位置


    ``` text
    -----
    |xxx|----o (TEXT_LEFT)
    -----

         -----
    o----|xxx| (TEXT_RIGHT)
         -----

    ----------
    |XXXXXXXX| (DEFAULT)
    ----------
    ```

    - DEFAULT
    - TEXT_UP
    - TEXT_RIGHT
    - TEXT_DOWN
    - TEXT_LEFT
    """

    DEFAULT = 0
    TEXT_UP = 1
    TEXT_RIGHT = 2
    TEXT_DOWN = 3
    TEXT_LEFT = 4


class InteractiveNodeJumpingType(enum.Enum):
    """
    对下一节点的跳转的方式

    - ASK    : 选择
    - DEFAULT: 跳转到默认节点
    - READY  : 选择(只有一个选择)
    """

    READY = 1
    DEFAULT = 0
    ASK = 2


class InteractiveVariable:
    """
    互动节点的变量
    """

    def __init__(
        self, name: str, var_id: str, var_value: int, show: bool = False, random: bool = False
    ):
        """
        Args:
            name      (str)  : 变量名
            var_id    (str)  : 变量 id
            var_value (int)  : 变量的值
            show      (bool) : 是否显示
            random    (bool) : 是否为随机值(1-100)
        """
        self.__var_id = var_id
        self.__var_value = var_value
        self.__name = name
        self.__is_show = show
        self.__random = random

    def get_id(self) -> str:
        return self.__var_id

    def refresh_value(self) -> None:
        """
        刷新变量数值
        """
        if self.is_random():
            self.__var_value = int(rand(0, 100))

    def get_value(self) -> int:
        return self.__var_value

    def is_show(self) -> bool:
        return self.__is_show

    def is_random(self) -> bool:
        return self.__random

    def get_name(self) -> str:
        return self.__name

    def __str__(self):
        return f"{self.__name} {self.__var_value}"


class InteractiveButton:
    """
    互动视频节点按钮类
    """

    def __init__(
        self, text: str, x: int, y: int, align: Union[InteractiveButtonAlign, int] = InteractiveButtonAlign.DEFAULT
    ):
        """
        Args:
            text  (str)                         : 文字
            x     (int)                         : x 轴
            y     (int)                         : y 轴
            align (InteractiveButtonAlign | int): 按钮的文字在按钮中的位置
        """
        self.__text = text
        self.__pos = (x, y)
        if isinstance(align, InteractiveButtonAlign):
            align = align.value
        self.__align = align

    def get_text(self) -> str:
        return self.__text

    def get_align(self) -> int:
        return self.__align # type: ignore

    def get_pos(self) -> Tuple[int, int]:
        return self.__pos

    def __str__(self):
        return f"{self.__text} {self.__pos}"


class InteractiveJumpingCondition:
    """
    节点跳转的公式，只有公式成立才会跳转
    """

    def __init__(self, var: List[InteractiveVariable] = [], condition: str = "True"):
        """
        Args:
            var       (List[InteractiveVariable]): 所有变量
            condition (str)                      : 公式
        """
        self.__vars = var
        self.__command = condition

    def get_result(self) -> bool:
        """
        计算公式获得结果

        Returns:
            bool: 是否成立
        """
        if self.__command == "":
            return True
        command = copy.copy(self.__command)
        for var in self.__vars:
            var_name = var.get_id()
            var_value = var.get_value()
            command = command.replace(var_name, str(var_value))
        command = command.replace("&&", " and ")
        command = command.replace("||", " or ")
        command = command.replace("!", " not ")
        command = command.replace("===", "==")
        command = command.replace("!==", "!=")
        command = command.replace("true", "True")
        command = command.replace("false", "False")
        return eval(command)

    def __str__(self):
        return f"{self.__command}"

class InteractiveJumpingCommand:
    """
    节点跳转对变量的操作
    """
    def __init__(self, var: List[InteractiveVariable] = [], command: str = ""):
        """
        Args:
            var       (List[InteractiveVariable]): 所有变量
            command   (str)                      : 公式
        """
        self.__vars = var
        self.__command = command

    def run_command(self) -> List["InteractiveVariable"]:
        """
        执行操作

        Returns:
            List[InteractiveVariable]
        """
        if self.__command == "":
            return self.__vars
        for code in self.__command.split(";"):
            var_name_ = code.split("=")[0]
            var_new_value = code.split("=")[1]
            for var in self.__vars:
                var_name = var.get_id()
                var_value = var.get_value()
                var_new_value = var_new_value.replace(var_name, str(var_value))
            var_new_value_calc = eval(var_new_value)
            for var in self.__vars:
                if var.get_id() == var_name_:
                    var._InteractiveVariable__var_value = var_new_value_calc # type: ignore
        return self.__vars

class InteractiveNode:
    """
    互动视频节点类
    """

    def __init__(
        self,
        video: "InteractiveVideo",
        node_id: int,
        cid: int,
        vars: List[InteractiveVariable],
        button: Union[InteractiveButton, None] = None,
        condition: InteractiveJumpingCondition = InteractiveJumpingCondition(),
        native_command: InteractiveJumpingCommand = InteractiveJumpingCommand(),
        is_default: bool = False,
    ):
        """
        Args:
            video          (InteractiveVideo)           : 视频类
            node_id        (int)                        : 节点 id
            cid            (int)                        : CID
            vars           (List[InteractiveVariable])  : 变量
            button         (InteractiveButton)          : 对应的按钮
            condition      (InteractiveJumpingCondition): 跳转公式
            native_command (InteractiveJumpingCommand)  : 跳转时变量操作
            is_default     (bool)                       : 是不是默认的跳转的节点
        """
        self.__parent = video
        self.__id = node_id
        self.__cid = cid
        self.__button = button
        self.__jumping_command = condition
        self.__is_default = is_default
        self.__vars = vars
        self.__command = native_command
        self.__vars = self.__command.run_command()

    async def get_vars(self) -> List[InteractiveVariable]:
        """
        获取节点的所有变量

        Returns:
            List[InteractiveVariable]: 节点的所有变量
        """
        return self.__vars

    async def get_children(self) -> List["InteractiveNode"]:
        """
        获取节点的所有子节点

        Returns:
            List[InteractiveNode]: 所有子节点
        """
        edge_info = await self.__parent.get_edge_info(self.__id)
        nodes = []
        for node in edge_info["edges"]["questions"][0]["choices"]:
            node_id = node["id"]
            node_cid = node["cid"]
            if "text_align" in node.keys():
                text_align = node["text_align"]
            else:
                text_align = 0
            if "option" in node.keys():
                node_button = InteractiveButton(
                    node["option"], node.get("x"), node.get("y"), text_align
                )
            else:
                node_button = None
            node_condition = InteractiveJumpingCondition(
                await self.get_vars(), node["condition"]
            )
            node_command = InteractiveJumpingCommand(
                await self.get_vars(), node["native_action"]
            )
            if "is_default" in node.keys():
                node_is_default = node["is_default"]
            else:
                node_is_default = False
            node_vars = copy.deepcopy(await self.get_vars())
            nodes.append(InteractiveNode(
                self.__parent,
                node_id,
                node_cid,
                node_vars,
                node_button,
                node_condition,
                node_command,
                node_is_default,
            ))
        return nodes

    def is_default(self) -> bool:
        return self.__is_default

    async def get_jumping_type(self) -> int:
        """
        获取子节点跳转方式 (参考 InteractiveNodeJumpingType)
        """
        edge_info = await self.__parent.get_edge_info(self.__id)
        return edge_info["edges"]["questions"][0]["type"]

    def get_node_id(self) -> int:
        return self.__id

    def get_cid(self) -> int:
        return self.__cid

    def get_self_button(self) -> "InteractiveButton":
        if self.__button == None:
            return InteractiveButton("", -1, -1)
        return self.__button

    def get_jumping_condition(self) -> "InteractiveJumpingCondition":
        return self.__jumping_command

    def get_video(self) -> "InteractiveVideo":
        return self.__parent

    async def get_info(self) -> dict:
        """
        获取节点的简介

        Returns:
            dict: 调用 API 返回的结果
        """
        return await self.__parent.get_edge_info(self.__id)

    def __str__(self):
        return f"{self.get_node_id()}"


class InteractiveGraph:
    """
    情节树类
    """

    def __init__(self, video: "InteractiveVideo", skin: dict, root_cid: int):
        """
        Args:
            video    (InteractiveVideo): 互动视频类
            skin     (dict)            : 样式
            root_cid (int)             : 根节点 CID
        """
        self.__parent = video
        self.__skin = skin
        self.__node = InteractiveNode(self.__parent, 1, root_cid, [])

    def get_video(self) -> "InteractiveVideo":
        return self.__parent

    def get_skin(self) -> dict:
        return self.__skin

    async def get_root_node(self) -> "InteractiveNode":
        """
        获取根节点

        Returns:
            InteractiveNode: 根节点
        """
        edge_info = await self.__parent.get_edge_info(None)
        if "hidden_vars" in edge_info.keys():
            node_vars = edge_info["hidden_vars"]
        else:
            node_vars = []
        var_list = []
        for var in node_vars:
            var_value = var["value"]
            var_name = var["name"]
            var_show = var["is_show"]
            var_id = var["id_v2"]
            if var["type"] == 2:
                random = True
            else:
                random = False
            var_list.append(
                InteractiveVariable(var_name, var_id, var_value, var_show, random)
            )
        self.__node._InteractiveNode__command = InteractiveJumpingCommand( # type: ignore
            var_list
        )
        self.__node._InteractiveNode__vars = var_list # type: ignore
        return self.__node

    async def get_children(self) -> List["InteractiveNode"]:
        """
        获取子节点

        Returns:
            List[InteractiveNode]: 子节点
        """
        return await self.__node.get_children()


class InteractiveVideo(Video):
    """
    互动视频类
    """

    def __init__(self, bvid = None, aid = None, credential=None):
        super().__init__(bvid, aid, credential)

    async def up_get_ivideo_pages(self) -> dict:
        """
        获取交互视频的分 P 信息。up 主需要拥有视频所有权。

        Returns:
            dict: 调用 API 返回的结果
        """
        credential = self.credential if self.credential else Credential()
        url = API["info"]["videolist"]["url"]
        params = {"bvid": self.get_bvid()}
        return await request("GET", url=url, params=params, credential=credential)

    async def up_submit_story_tree(self, story_tree: str) -> dict:
        """
        上传交互视频的情节树。up 主需要拥有视频所有权。

        Args:
            story_tree (str): 情节树的描述，参考 bilibili_storytree.StoryGraph, 需要 Serialize 这个结构

        Returns:
            dict: 调用 API 返回的结果
        """
        credential = self.credential if self.credential else Credential()
        url = API["operate"]["savestory"]["url"]
        form_data = {"preview": "0", "data": story_tree, "csrf": credential.bili_jct}
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://member.bilibili.com",
            "Content-Encoding": "gzip, deflate, br",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json, text/plain, */*",
        }
        data = parse.urlencode(form_data)
        return await request(
            "POST",
            url=url,
            data=data,
            headers=headers,
            no_csrf=True,
            credential=credential,
        )

    async def get_graph_version(self) -> int:
        """
        获取剧情图版本号，仅供 `get_edge_info()` 使用。

        Returns:
            int: 剧情图版本号
        """
        # 取得初始顶点 cid
        bvid = self.get_bvid()
        credential = self.credential if self.credential else Credential()
        v = Video(bvid=bvid, credential=credential)
        page_list = await v.get_pages()
        cid = page_list[0]["cid"]

        # 获取剧情图版本号
        api = "https://api.bilibili.com/x/player/v2"
        params = {"bvid": bvid, "cid": cid}

        resp = await request("GET", api, params, credential=credential)
        return resp["interaction"]["graph_version"]

    async def get_edge_info(self, edge_id: Union[int, None] = None):
        """
        获取剧情图节点信息

        Args:
            edge_id       (int, optional)       : 节点 ID，为 None 时获取根节点信息. Defaults to None.

        Returns:
            dict: 调用 API 返回的结果
        """
        bvid = self.get_bvid()
        credential = self.credential if self.credential is not None else Credential()

        url = API["info"]["edge_info"]["url"]
        params = {"bvid": bvid, "graph_version": (await self.get_graph_version())}

        if edge_id is not None:
            params["edge_id"] = edge_id

        return await request("GET", url, params, credential=credential)

    async def get_cid(self) -> int:
        """
        获取稿件 cid
        """
        return await super().get_cid(0)

    async def get_graph(self):
        """
        获取稿件情节树

        Returns:
            InteractiveGraph: 情节树
        """
        edge_info = await self.get_edge_info(1)
        cid = await self.get_cid()
        return InteractiveGraph(self, edge_info["edges"]["skin"], cid)


class InteractiveVideoDownloaderEvents(enum.Enum):
    """
    互动视频下载器事件枚举

    + START           : 开始下载
    + GET             : 获取到节点信息
    + PREPARE_DOWNLOAD: 准备下载节点
    (以下为内建下载函数发布事件)
    + DOWNLOAD_START  : 开始下载单个文件
    + DOWNLOAD_PART   : 文件分块部分完成
    + DOWNLOAD_SUCCESS: 完成下载
    (END)
    + PACKAGING       : 打包文件
    + SUCCESS         : 完成下载
    + ABORTED         : 终止下载
    + FAILED          : 下载失败
    """
    START = "START"
    GET = "GET"
    DOWNLOAD_START = "DOWNLOAD_START"
    DOWNLOAD_PART = "DOWNLOAD_PART"
    DOWNLOAD_SUCCESS = "DOWNLOAD_SUCCESS"
    PACKAGING = "PACKAGING"
    SUCCESS = "SUCCESS"
    ABORTED = "ABORTED"
    FAILED = "FAILED"


class InteractiveVideoDownloader(AsyncEvent):
    """
    互动视频下载类(下载格式：ivi)
    """
    def __init__(self, video: InteractiveVideo, out: str = "", self_download_func: Union[Callable, None] = None):
        """
        Args:
            video (InteractiveVideo)             : 互动视频类
            out   (str)                          : 输出文件地址
            self_download_func (Coroutine | None): 自定义下载函数（需 async 函数）

        `self_download_func` 函数应接受两个参数（第一个是下载 URL，第二个是输出地址（精确至文件名））
        """
        super().__init__()
        self.__video = video
        if self_download_func == None:
            self.__download_func = self.__download
        else:
            self.__download_func = self_download_func
        self.__task = None
        self.__out = out

    async def __download(self, url: str, out: str) -> None:
        resp = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.bilibili.com"},
            proxies={"all://": settings.proxy},
            stream=True,
        )
        resp.raise_for_status()

        if os.path.exists(out):
            os.remove(out)

        parent = os.path.dirname(out)
        if not os.path.exists(parent):
            os.mkdir(parent)

        self.dispatch("DOWNLOAD_START", {"url": url, "out": out})

        all_length = int(resp.headers["Content-Length"])
        parts = all_length // 1024 + (1 if all_length % 1024 != 0 else 0)
        cnt = 0
        start_time = time.perf_counter()

        with open(out, "wb") as f:
            for chunk in resp.iter_content(1024):
                cnt += 1
                self.dispatch("DOWNLOAD_PART", {"done": cnt, "total": parts, "time": int(time.perf_counter() - start_time)})
                f.write(chunk)

        self.dispatch("DOWNLOAD_SUCCESS")

    async def __main(self) -> None:
        # 初始化
        self.dispatch("START")
        if self.__out == "": self.__out = self.__video.get_bvid() + ".ivi"
        if self.__out.endswith(".ivi"): self.__out = self.__out.rstrip(".ivi")
        if os.path.exists(self.__out + ".ivi"):
            os.remove(self.__out + ".ivi")
        tmp_dir_name = self.__out + ".tmp"
        if not os.path.exists(tmp_dir_name):
            os.mkdir(tmp_dir_name)
        def createEdge(edge_id: int):
            """
            创建节点信息到 edges_info
            """
            edges_info[edge_id] = {
                "title": None,
                "cid": None,
                "button": None,
                "condition": None,
                "jump_type": None,
                "is_default": None,
                "command": None,
                "sub": []
            }
        def var2dict(var: InteractiveVariable):
            return {
                "name": var.get_name(),
                "id": var.get_id(),
                "value": var.get_value(),
                "show": var.is_show(),
                "random": var.is_random()
            }


        # 存储顶点信息
        edges_info = {}

        # 使用队列来遍历剧情图，初始为 None 是为了从初始顶点开始
        queue: List[InteractiveNode] = [await (await self.__video.get_graph()).get_root_node()]

        # 设置初始顶点
        n = await (await self.__video.get_graph()).get_root_node()
        if n.get_node_id() not in edges_info:
            createEdge(n.get_node_id())
        edges_info[n.get_node_id()]['cid'] = n.get_cid()
        edges_info[n.get_node_id()]['button'] = {
            "text": n.get_self_button().get_text(),
            "align": n.get_self_button().get_align(),
            "pos": (n.get_self_button().get_pos())
        }
        edges_info[n.get_node_id()]['vars'] = [var2dict(var) for var in (await n.get_vars())]
        edges_info[n.get_node_id()]['condition'] = n.get_jumping_condition()._InteractiveJumpingCondition__command,  # type: ignore
        edges_info[n.get_node_id()]['jump_type'] = 0
        edges_info[n.get_node_id()]['is_default'] = True
        edges_info[n.get_node_id()]['command'] = n._InteractiveNode__command._InteractiveJumpingCommand__command # type: ignore

        while queue:
            # 出队
            now_node = queue.pop()

            if now_node.get_node_id() in edges_info and edges_info[now_node.get_node_id()]['title'] is not None and edges_info[now_node.get_node_id()]['cid'] is not None:
                # 该情况为已获取到所有信息，说明是跳转到之前已处理的顶点，不作处理
                continue

            # 获取顶点信息，最大重试 3 次
            retry = 3
            while True:
                try:
                    node = await now_node.get_info()
                    self.dispatch("GET", {"title": node['title'], "node_id": now_node.get_node_id()})
                    break
                except Exception as e:
                    retry -= 1
                    if retry < 0:
                        raise e

            # 下载节点

            # 检查节顶点是否在 edges_info 中，本次步骤得到 title 信息
            if node['edge_id'] not in edges_info:
                # 不在，新建
                createEdge(node['edge_id'])

            # 设置 title
            edges_info[node['edge_id']]['title'] = node['title']

            # 无可达顶点，即不能再往下走了，类似树的叶子节点
            if 'questions' not in node['edges']:
                continue

            # 遍历所有可达顶点
            for n in (await now_node.get_children()):
                # 该步骤获取顶点的 cid（视频分 P 的 ID）
                if n.get_node_id() not in edges_info:
                    createEdge(n.get_node_id())
                edges_info[n.get_node_id()]['cid'] = n.get_cid()
                edges_info[n.get_node_id()]['button'] = {
                    "text": n.get_self_button().get_text(),
                    "align": n.get_self_button().get_align(),
                    "pos": n.get_self_button().get_pos()
                }
                def var2dict(var: InteractiveVariable):
                    return {
                        "name": var.get_name(),
                        "id": var.get_id(),
                        "value": var.get_value(),
                        "show": var.is_show(),
                        "random": var.is_random()
                    }
                edges_info[n.get_node_id()]['condition'] = n.get_jumping_condition()._InteractiveJumpingCondition__command # type: ignore
                edges_info[n.get_node_id()]['jump_type'] = await now_node.get_jumping_type()
                edges_info[n.get_node_id()]['is_default'] = n.is_default()
                edges_info[n.get_node_id()]['command'] = n._InteractiveNode__command._InteractiveJumpingCommand__command # type: ignore
                edges_info[now_node.get_node_id()]['sub'] = [n.get_node_id() for n in await now_node.get_children()]
                # 所有可达顶点 ID 入队
                queue.insert(0, n)

        json.dump(edges_info, open(tmp_dir_name + "/ivideo.json", "w+", encoding = "utf-8"), indent = 2)
        json.dump({
            "bvid": self.__video.get_bvid(),
            "title": (await self.__video.get_info())["title"]
        }, open(tmp_dir_name + "/bilivideo.json", "w+", encoding = "utf-8"), indent = 2)

        for key, item in edges_info.items():
            self.dispatch("PREPARE_DOWNLOAD", {"node_id": int(key), "cid": item["cid"]})
            cid = item["cid"]
            url = await self.__video.get_download_url(cid = cid, html5 = True)
            await self.__download_func(url["durl"][0]["url"], tmp_dir_name + "/" + str(cid) + ".mp4")

        self.dispatch("PREPARE_DOWNLOAD", {"node_id": 1, "cid": await self.__video.get_cid()})
        cid = await self.__video.get_cid()
        url = await self.__video.get_download_url(cid = cid, html5 = True)
        await self.__download_func(url["durl"][0]["url"], tmp_dir_name + "/" + str(cid) + ".mp4")

        self.dispatch("PACKAGING")
        zip = zipfile.ZipFile(open(self.__out + ".ivi", "wb+"), mode = "w", compression = zipfile.ZIP_DEFLATED)  # outFullName为压缩文件的完整路径
        for path, dirnames, filenames in os.walk(tmp_dir_name):
            # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
            fpath = path.replace(tmp_dir_name, '')

            for filename in filenames:
                zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
        zip.close()
        shutil.rmtree(tmp_dir_name)
        self.dispatch("SUCCESS")

    async def start(self) -> None:
        """
        开始下载
        """
        task = create_task(self.__main())
        self.__task = task

        try:
            result = await task
            self.__task = None
            return result
        except CancelledError:
            # 忽略 task 取消异常
            pass
        except Exception as e:
            self.dispatch("FAILED", {"err": e})
            raise e

    async def abort(self) -> None:
        """
        中断下载
        """
        if self.__task:
            self.__task.cancel("用户手动取消")

        self.dispatch("ABORTED", None)

def get_ivi_file_meta(path: str) -> dict:
    """
    获取 ivi 文件信息

    Args:
        path (str): 文件地址

    Returns:
        dict: 文件信息
    """
    ivi = zipfile.ZipFile(open(path, "rb"))
    info = ivi.open("bilivideo.json").read()
    return json.loads(info)
