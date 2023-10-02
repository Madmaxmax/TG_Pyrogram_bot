import os

# Получаем количество доступных потоков
num_threads = os.cpu_count()

print(f"Количество доступных потоков на устройстве: {num_threads}")

