from guardin_mind import Mind
import asyncio

mind = Mind() # Создаем основной класс Mind
hello_world = mind.HelloWorld() # Ищем майндер HelloWorld

# Синхронный запрос
result = hello_world.ask_sync(f"Sending to sync") # Синхронно отправляем запрос и получаем ответ

print(result)

# Асинхронный запрос
result = asyncio.run(hello_world.ask_async(f"Sending to async")) # Асинхронно отправляем запрос и получаем ответ

print(result)