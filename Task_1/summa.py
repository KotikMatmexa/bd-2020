import time
import numpy as np
import threading
import mmap
import concurrent.futures as ft
import multiprocessing


#Простое последовательное суммирование
def summ_sequential():
    with open('numbers.txt', 'r+b') as f:
        buf = f.read()
        numbers = np.frombuffer(buf, dtype=np.dtype('uint32').newbyteorder('B')) #считывание всех данных
    summ = 0 
    for i in numbers:
        summ += i
    return(summ)

#Суммирование с использованием threading и mmap
def summ_maped_threads(results, i,  n1, n2):  
    with open('numbers.txt', 'r+b') as f:
        with mmap.mmap(f.fileno(), length=(n2-n1)*4, offset=n1, access=mmap.ACCESS_READ) as mm: #Мапинг части файла для одного потока
            numbers = np.frombuffer(mm, dtype=np.dtype('uint32').newbyteorder('B')) #считывание данных для потока
            for number in numbers: #т.к. threading не поддерживает return для функций, результат записывается в список, с числом элементов равным числу потоков
                results[i] += number
            
def summa(chunk):
    sum = 0 
    for i in chunk:
        sum += i
    return(sum)
def summ_concfutures(num_workers):
    summ = 0        
    with open('numbers.txt', 'r+b') as f:
        with mmap.mmap(f.fileno(), length=0, offset=0, access=mmap.ACCESS_READ) as mm: #Мапинг всего файла
            numbers = np.frombuffer(mm, dtype=np.dtype('uint32').newbyteorder('B')) #считывание данных для потока
            split = len(numbers)//num_workers #Число разбиений
            number_list = [numbers[i:i+split] for i in range(0, len(numbers), split)] #Разбиение массива чисел на split частей
            with ft.ThreadPoolExecutor(max_workers=num_workers) as executor: #запуск потоков
                futures = {executor.submit(summa, chunk): chunk for chunk in number_list}
                for future in ft.as_completed(futures):
                    summ += future.result() #суммирование результатов
    return(summ)


def summ_multi(num_processor):
    summ = 0          
    numbers = np.fromfile('numbers.txt', dtype=np.uint32) #считывание данных стандартной процедурой numpy
    split = len(numbers)//num_processor #Число разбиений
    number_list = [numbers[i:i+split] for i in range(0, len(numbers), split)] #Разбиение массива чисел на split частей
    with multiprocessing.Pool(num_processor) as mp:
        results = mp.map(summa,number_list)
    return(sum(results))
        
                    
  
if __name__ == '__main__':
    #Простое последовательное суммирование
    start = time.time()
    res = summ_sequential()
    #print('Сумма чисел: '+ str(res))
    end = time.time()
    print('Время выполения при последовательном чтении: '+str(end - start))  

    #потоки и мапинг
    n1 = 0 #стартовая точка - начало файла
    T = 256 #число потоков
    results = [0] * T
    deltaN = int(len(np.fromfile('numbers.txt', dtype=np.uint32))/T) #разбиение файла на T равных частей
    threads = []
    #запуск таймера для получение времени при использовании многопоточности
    start = time.time()
    for i in range(T):
        n2 = n1 + deltaN #получение сегмента для потока
        t = threading.Thread(target=summ_maped_threads, args=(results, i, n1, n2)) #создание потока суммирующего числа сегмента
        threads.append( t ) #добавление потока в список
        t.start() #старт потока      
        n1 = n2 #переназначение начала файла
    for t in threads:
        t.join() #завершение потоков
    #print(sum(results)) 
    end = time.time()
    print('Время выполения с использованием ' +str(T)+' потоков и mmap: '+str(end - start))   
    
    #Через futures
    start = time.time()
    res = summ_concfutures(8)
    #print('Сумма чисел: '+ str(res))
    end = time.time()
    print('Время выполения с помощью mmap и futures с 8 workers: '+str(end - start))  
        
    #Через multiprocessing без mmap
    start = time.time()
    res = summ_multi(8)
    #print('Сумма чисел: '+ str(res))
    end = time.time()
    print('Время выполения с помощью multiprocessing без mmap на 8 процессов: '+str(end - start))  


    

    