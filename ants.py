import numpy as np

class City(object):
    def __init__ (self, city_id):
        self.id = city_id
        
    def __str__ (self):
        return self.id

class Ant(object):
    def __init__(self, start_city):
        self.cur_city = start_city
        self.path = [start_city]
        self.walk_lenght = 0

    def reset(self, city):
        self.cur_city = city
        self.path = [city]
        self.walk_lenght = 0

    def move_to_city(self, world, new_city):
        self.path.append(new_city)
        self.walk_lenght += world.graph_matrix[self.cur_city.id,new_city.id]
        if len(self.path) == world.cities_cnt:
            self.walk_lenght += world.graph_matrix[self.path[-1].id, self.path[0].id]
        self.cur_city = new_city

    def can_move(self, world):
        return len(self.path) < world.cities_cnt

class World(object):
    def __init__(self, a):
        self.graph_matrix = a
        self.cities_cnt = self.graph_matrix.shape[0] #количество городов
        self.__start_city_id = 1 #координаты начальной и конечной точки
        self.__ant_cnt = 4 #количество муравьёв
        self.__iterations_cnt = 2000 #количество итераций
        self.__alpha = 1 #коэффициент привлекательности запаха
        self.__beta = 2 #коэффициент привлекательности расстояния
        self.__rho = 0.5 #коэффициент испарения ферромонов
        self.__Q = 1.0 #количество выпускаемых ферромонов
        self.__ph = self.__Q / (self.cities_cnt * 2000) #начальное значение ферромонов
        self.__pherro = np.full(self.graph_matrix.shape, self.__ph) #матрица ферромонов, заполненная изначальным значением ферромонов       
        self.__cities = [] 
        self.__best_way_lngt=1e+6
        self.__best_ant = None
        for i in range(self.cities_cnt):
            self.__cities.append(City(i))
        self.__ants = []
        for i in range(self.__ant_cnt):
            self.__ants.append(Ant(self.__cities[self.__start_city_id])) #муравьев рассадил в стартовый город

    
    def __restart_ants(self):
        for ant in self.__ants:
            if ant.walk_lenght < self.__best_way_lngt:  
                self.__best_way_lngt = ant.walk_lenght  #фиксируем текущий лучший путь
                self.__best_ant = ant                   #и лучшего муравья
            ant.reset(self.__cities[self.__start_city_id]) #всех муравьев возвращаем в изначальный город
            
    def __move_your_ant(self):
        moving = 0
        for ant in self.__ants:
            if ant.can_move(self):
                next_city = self.__select_next_city(ant)
                ant.move_to_city(self, next_city)
                moving += 1
        return moving
  

    def __select_next_city(self, ant):
        denom = 0.0 #значение знаменателя вероятности
        not_visited = [] #список непосещенных городов
        for next_city in self.__cities:
            if next_city not in ant.path:#ищем непосещенные города
                tau = self.__pherro[ant.cur_city.id, next_city.id]
                theta = self.graph_matrix[ant.cur_city.id, next_city.id]
                ap = (tau ** self.__alpha) * (theta ** self.__beta) #числитель вероятности перемещения в город next_city
                not_visited.append((next_city, ap)) #формируем пары для 
                denom += ap #подсчитываем знаменатель       
        not_visited = [(val, ap / denom) for (val, ap) in not_visited] # делим все значения на знаменатель
        r = np.random.random() # реализация вероятности перехода в другой город
        cur_probability = 0
        cur_val = None
        for val, probability in not_visited:
            cur_val = val
            cur_probability += probability
            if r <= cur_probability:
                break
        return cur_val

    def __update_roads(self):
        for ant in self.__ants: #обновляем последние куски пути, которые прошли муравьи
            pheromove_amount = 1 / ant.walk_lenght

            for i in range(self.cities_cnt):
                if i == self.cities_cnt - 1:
                    from_city = ant.path[i]
                    to_city = ant.path[0]
                else:
                    from_city = ant.path[i]
                    to_city = ant.path[i + 1]
                
                if from_city != to_city:
                    self.__pherro[from_city.id, to_city.id] =  self.__pherro[from_city.id, to_city.id] * (1.0-self.__rho) + pheromove_amount
                    self.__pherro[to_city.id, from_city.id] = self.__pherro[from_city.id, to_city.id]


    def calculate(self):
        cur_time = 0
        while cur_time < self.__iterations_cnt:
            cur_time += 1
            if self.__move_your_ant() == 0:
                self.__update_roads()
                cur_time != self.__iterations_cnt and self.__restart_ants()

        return self.__best_way_lngt     

if __name__ == '__main__':
    np.random.seed = 7
    a = np.random.randint(1, high=50, size=(20,20))
    for i in range(a.shape[0]):
        for j in range(a.shape[0]):
            if i == j:
                a[i,j]=0
            else:
                a[i,j]=a[j,i]
    
    w = World(a)
    print(w.calculate())