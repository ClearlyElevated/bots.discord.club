import rethinkdb as rdb


rdb.set_loop_type("asyncio")
con = None

host, port, database = "localhost", 28015, "botlist"
table_setup = {
    "botlist": {
        "bots": []
    }
}

secondary_keys = ["timestamp"]

async def setup():
    global con
    con = await rdb.connect(host=host, port=port, db=database)

    for db_name, tables in table_setup.items():
        if db_name not in await rdb.db_list().run(con):
            await rdb.db_create(db_name).run(con)

        db = rdb.db(db_name)
        for table_name, data in tables.items():
            if table_name not in await db.table_list().run(con):
                await db.table_create(table_name).run(con)

                await db.table(table_name).insert(data).run(con)

            for key in secondary_keys:
                try:
                    await db.table(table_name).index_create(key).run(con)
                except:
                    pass


async def cursor_to_list(async_cursor):
    ret = []
    while (await async_cursor.fetch_next()):
        item = await async_cursor.next()
        ret.append(item)

    return ret