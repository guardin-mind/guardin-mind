from guardin_mind import Mind
from guardin_mind.minders.HelloWorld.minder import HelloWorld
import asyncio
import threading

mind = Mind(debug=True)
io = mind.load(HelloWorld)

async def main():
    coros = [io.ask_async(f"Hello from call {i}") for i in range(5)]

    # Запускаем все одновременно
    results = await asyncio.gather(*coros)

    print("All done:")
    print(results)

def thread_test():
    def worker(i):
        answer = io.ask_sync(f"Hello from thread call {i}")
        print(f"\nThread {i} got answer: {answer}")

    threads = []
    for i in range(5):
        t = threading.Thread(target=worker, args=(i,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
    print("Threading All done")

if __name__ == "__main__":
    asyncio.run(main())
    thread_test()