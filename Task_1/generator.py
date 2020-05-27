from numpy.random import randint
from numpy import uint32

def generate(size):
  #Генерация случайных чисел от 0 до максимального uint32 с размером size
  numbers = randint(0, high=4294967295, size=size, dtype = uint32)  
  with open('numbers.txt', 'wb') as f:
      for item in numbers:
          #Запись данных для 
          f.write(item.tobytes())
if __name__ == '__main__':
    #создание файла размером: 2*1024*1024*1024/4, деление на 4 т.к. каждое из чисел в формате uint32 занимает 4 байта
    generate(2*1024*1024*256)
    