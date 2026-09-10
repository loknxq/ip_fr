def show_records(records):
    num=0
    for i in records:
        num+=1
        print(str(num)+"."+i)

recordnames=["пл1","пл2","пл3"]
collection_contenst=[[1],[2,3]]
collections=["Коллекция 1","Коллекция 2"]
action0=int(input("Выберите действие:\n1. Показать все коллекции.\n2. Добавить пластинку.\n3. Добавить коллекцию.\n4. Выход\n(Введите номер действия)\n"))
if action0==1:
    num=0
    for i in collections:
        num+=1
        print(str(num)+"."+i)
    num=0
    action1=int(input("Выберите действие:\n1. Показать содержимое коллекции.\n2. Выход\n(Введите номер действия)\n"))
    if action1==1:
        action2=int(input("Введите номер коллекции.\n"))
        for i in collection_contenst[action2-1]:
            print(recordnames[i-1])
    else:
        print("Пока!")
if action0==2:
    recordnames+=[input("Введите название пластинки:\n")]
    print("Пластинка добавлена.")
if action0==3:
    collections+=[input("Введите название коллекции:\n")]
    new_record=[]
    filler=-1
    print("Введите поочереди номера пластиноккогда закончите, введите 0")
    show_records(recordnames)
    while filler!=0:
        filler=int(input())
        if filler!=0:
            new_record+=[filler]
    collection_contenst.append(new_record)
    print("Коллекция добавлена.")
if action0==4:
    print("Пока!")