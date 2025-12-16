def binary_find(lst: list, value: int) -> int: #Функция вернет нам индекс ввиде целого числа
    if not lst:
        return None #Если список пустой, то там нечего искать
    
    mid = len(lst) // 2 #Находим значение в середине без остатка
    mid_value = lst[mid]

    if value == mid_value:
        return mid #Проверка на совпадение
    elif value < mid_value:
        return binary_find(lst[:mid], value) #Если значение меньше, то функция запускается снова, но в списке будет только первая половина
    else:
        result = binary_find(lst[mid + 1:], value) #Если значение больше, то функция запускается снова, но в списке будет вторая половина
        return result + mid + 1 if result is not None else None #Если он не найдет, то вернется None (ничего)