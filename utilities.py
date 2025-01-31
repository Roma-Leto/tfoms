import time

# region Декораторы

def timer(func):
    """
    Декоратор для измерения времени выполнения функции
    :param func: объект измерений, функция
    :return: 0
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Засекаем время начала
        result = func(*args, **kwargs)  # Вызов оригинальной функции
        end_time = time.time()  # Засекаем время окончания
        print(f"Функция {func.__name__} выполнилась за {end_time - start_time:.4f} секунд.")
        return result
    return wrapper

# endregion Декораторы