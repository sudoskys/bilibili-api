# bilibili_api.search

from bilibili_api import search


async def test_a_search():
    return await search.search("这是他的笑容发生的变化")


async def test_b_search_by_type():
    return await search.search_by_type("丸子叨叨叨", search.SearchObjectType.USER)


async def test_c_get_hot_search_keywords():
    return await search.get_hot_search_keywords()


async def test_d_get_default_search_keyword():
    return await search.get_default_search_keyword()


async def test_e_get_suggest_keywords():
    return await search.get_suggest_keywords("gswdm")


async def test_f_search_by_order():
    return await search.search_by_type(
        "小马宝莉",
        search_type = search.SearchObjectType.VIDEO,
        order_type = search.OrderVideo.SCORES,
        time_range = 10,
        topic_type = 25,
        page = 1,
        debug_param_func = print,
    )


# from bilibili_api import sync
#
# res = sync(test_f_search_by_order())
# print(res)
