from django.core.exceptions import ValidationError
from datetime import datetime

def validate_tuple(value):
    if not isinstance(value, tuple):
        raise ValidationError('Ожидается кортеж')

    if len(value) != 15:
        raise ValidationError('Кортеж должен содержать 15 элементов')

    # Проверка типов данных для каждого элемента
    if not isinstance(value[0], (float, str)):  # Первый элемент может быть float или строкой, представляющей float
        raise ValidationError('Первый элемент должен быть числом с плавающей точкой или строкой, представляющей число')
    if isinstance(value[0], str):
        try:
            float(value[0])  # Проверяем, что строка может быть преобразована в float
        except ValueError:
            raise ValidationError('Первый элемент (строка) не может быть преобразован в число с плавающей точкой')

    if not isinstance(value[1], str):  # Второй элемент должен быть строкой
        raise ValidationError('Второй элемент должен быть строкой')

    if not isinstance(value[2], int):  # Третий элемент должен быть целым числом
        raise ValidationError('Третий элемент должен быть целым числом')

    if not isinstance(value[3], str):  # Четвёртый элемент должен быть строкой
        raise ValidationError('Четвёртый элемент должен быть строкой')

    if not isinstance(value[4], str):  # Пятый элемент должен быть строкой с датой в формате 'дд.мм.гггг'
        raise ValidationError('Пятый элемент должен быть строкой')
    try:
        datetime.strptime(value[4], '%d.%m.%Y')  # Проверка формата даты
    except ValueError:
        raise ValidationError('Пятый элемент (дата) должен быть в формате дд.мм.гггг')

    if not isinstance(value[5], str):  # Шестой элемент должен быть строкой
        raise ValidationError('Шестой элемент должен быть строкой')

    if not isinstance(value[6], str):  # Седьмой элемент должен быть строкой
        raise ValidationError('Седьмой элемент должен быть строкой')

    if not isinstance(value[7], str):  # Восьмой элемент должен быть строкой
        raise ValidationError('Восьмой элемент должен быть строкой')

    if not isinstance(value[8], str):  # Девятый элемент должен быть строкой
        raise ValidationError('Девятый элемент должен быть строкой')

    if not isinstance(value[9], str):  # Десятый элемент должен быть строкой с датой в формате 'дд.мм.гггг'
        raise ValidationError('Десятый элемент должен быть строкой')
    try:
        datetime.strptime(value[9], '%d.%m.%Y')  # Проверка формата даты
    except ValueError:
        raise ValidationError('Десятый элемент (дата) должен быть в формате дд.мм.гггг')

    if not isinstance(value[10], str):  # Одиннадцатый элемент должен быть строкой с датой в формате 'дд.мм.гггг'
        raise ValidationError('Одиннадцатый элемент должен быть строкой')
    try:
        datetime.strptime(value[10], '%d.%m.%Y')  # Проверка формата даты
    except ValueError:
        raise ValidationError('Одиннадцатый элемент (дата) должен быть в формате дд.мм.гггг')

    if not isinstance(value[11], str):  # Двенадцатый элемент должен быть строкой
        raise ValidationError('Двенадцатый элемент должен быть строкой')

    if not isinstance(value[12], int):  # Тринадцатый элемент должен быть целым числом
        raise ValidationError('Тринадцатый элемент должен быть целым числом')

    if not isinstance(value[13], (float, int)):  # Четырнадцатый элемент должен быть числом (float или int)
        raise ValidationError('Четырнадцатый элемент должен быть числом')

    if not isinstance(value[14], (float, int)):  # Пятнадцатый элемент должен быть числом (float или int)
        raise ValidationError('Пятнадцатый элемент должен быть числом')

# Пример использования
try:
    validate_tuple(('4.1081', 'ГОПЧЕНКО ДМИТРИЙ ВАЛЕРЬЕВИЧ', 7035935, 'случаев госпитализаций', '03.04.2009', '8798000046000059', 'Ростовская область', '(20)детской хирургии - (21)Детская хирургия', 'I86.1', '16.12.2024', '23.12.2024', '(101)Выписан', 1, 43203.4, 43203.4))
except ValidationError as e:
    print(e)