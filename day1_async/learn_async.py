import asyncio
import time

#%% funcs
async def task(task_name="", delay=2):
    start_t = time.time()
    await asyncio.sleep(delay)
    print(f"finish task[{task_name}], cost time:", time.time()-start_t)

async def slowly(task_name="", loop=int(1e8)):
    start_t = time.time()
    count = 0
    for _ in range(loop):
        count += 1
    print(f"finish slowly task[{task_name}], cost time:", time.time()-start_t)
    return count

#%% test funcs
def test1():
    """run asyn"""
    print("--- test1: run", "-"*40)
    asyncio.run(task("1"))

def test2():
    """gather 3 tasks"""
    print("--- test2: gather", "-"*40)
    async def tasks_gather():
        start_t = time.time()
        ret = await asyncio.gather(
            task("1",0.5), 
            task("2",1), 
            task("3",1.5)
        )
        print(f"finish all tasks, cost time:", time.time()-start_t)
        return ret

    asyncio.run(tasks_gather())

def test3():
    """create tasks"""
    print("--- test3: create_task", "-"*40)

    async def tasks_create():
        start_t = time.time()
        t1 = asyncio.create_task(task("1",0.5))
        t2 = asyncio.create_task(task("2",1))
        t3 = asyncio.create_task(task("3",1.5))

        await t1
        await t2
        await t3

        print(f"finish all tasks, cost time:", time.time()-start_t)
    
    asyncio.run(tasks_create())

def test4():
    print("--- test4: slowly tasks", "-"*40)
    async def gather_slowly():
        start_t = time.time()
        await asyncio.gather(
            slowly("1", int(0.5e8)), # 0.9
            slowly("2", int(1e8)), # 1.8
            slowly("3", int(1.5e8)), # 2.7
        )
        print(f"finish all tasks, cost time:", time.time()-start_t)
        # 0.9 + 1.8 + 2.7 = 5.4

    asyncio.run(gather_slowly())

def test5(mode=1):
    print(f"--- test5[{mode}]: mix tasks", "-"*40)
    async def mix_task(task_name="", lv=1, mode=mode):
        start_t = time.time()
        if mode == 1:
            await slowly(task_name, int(lv*1e8))
            await task(task_name, lv)
        else:
            await asyncio.gather(
                slowly(task_name, int(lv*1e8)),
                task(task_name, lv)
            )
        print(f"finish all mixed tasks[{task_name}], cost time:", time.time()-start_t)

    async def gather_mix():
        start_t = time.time()
        await asyncio.gather(
            mix_task("1", 0.5), # 0.9 | 0.5
            mix_task("2", 1), # 1.8 | 1.0
            mix_task("3", 1.5), # 2.7 | 1.5
        )
        print(f"finish all tasks, cost time:", time.time()-start_t)
        # 0.9 + 1.8 + 2.7 + 1.5 = 6.9

    asyncio.run(gather_mix())

#%% main
if __name__ == "__main__":
    print("start testing ...")
    start_t = time.time()

    # test1()
    # test2()
    # test3()
    # test4()
    test5(1)
    test5(2)

    print("="*50)
    print(f"finish all tests, cost time:", time.time()-start_t)
