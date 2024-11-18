from sys import argv
from time import sleep
from rich.console import Console
from random import randint
    
class SchedulerType():
    FIFO = "FIFO"
    SJF  = "SJF"
    STCF = "STCF"
    RR   = "RR"

colors = ["red", "blue", "green", "magenta", "cyan", "deep_pink1"]
console = Console()


class Task():
    def __init__(self, name: str, calc: int, enter: int, color:str="none"):
        self.calc = calc
        self.enter = enter
        self.arrive = 0
        self.worktime = 0
        self.finish = 0
        self.name = name

        if color == "none": 
            self.color = colors[randint(0, len(colors)-1)]
            colors.remove(self.color)
        else: self.color = color
    
    def pass_time(self):
        return self.finish-self.enter

    def answer_time(self):
        return self.arrive-self.enter
    
    def __str__(self):
        return f"{self.name}:  WT={self.worktime:2} ENTER={self.enter:2} ARRIVE={self.arrive:2} PT={self.pass_time():2} AT={self.answer_time():2}"

class Scheduler():
    def __init__(self, type: SchedulerType):
        self.tasks = []
        self._type = type
        self.time = 0
    

    def put(self, *tasks: Task):
        for task in tasks:
            self.tasks.append(task)


    def create_timeline(self):
        match self._type:
            case SchedulerType.FIFO: self.fifo()
            case SchedulerType.SJF:  self.sjf()
            case SchedulerType.STCF: self.stcf()
            case SchedulerType.RR:   self.rr()
    
    def print_timeline(self):
        get_arrive = lambda task: task.arrive
        console.print()
        for task in sorted(self.tasks, key=get_arrive):
            length = int((task.worktime*6-1))
            console.print('┃' + length*'░', end='', style=task.color)
        console.print('┃')
        for task in sorted(self.tasks, key=get_arrive):
            length = int((task.worktime*6-1)/2)-1
            console.print('┃' + length*'░' + f'▏{task.name}▕' + length*'░', end='', style=task.color)
        console.print('┃')
        for task in sorted(self.tasks, key=get_arrive):
            length = int((task.worktime*6-1))
            console.print('┃' + length*'░', end='', style=task.color)
        console.print('┃')
        
        for i in range(self.time+1):
            if i%2 == 0: print('+', end='')
            else: console.print('—————:—————', end='')
        console.print("——>")
        for i in range(self.time+1):
            if i%2 == 0: 
                if i < 10: print(f'{i} ', end='')
                else: console.print(i, end='')
            else: console.print('          ', end='')
        print('\n')

    def print_statistics(self):
        print(self._type)
        get_arrive = lambda task: task.arrive
        for task in sorted(self.tasks, key=get_arrive): print(task)
        print(f"PT_avg={sum(list(map(lambda task: task.pass_time(), self.tasks)))/len(self.tasks):2.2f}")
        print(f"AT_avg={sum(list(map(lambda task: task.answer_time(), self.tasks)))/len(self.tasks):2.2f}")
    
    def fifo(self):
        queue = []
        running: Task = None
        tasks_completed = 0

        while len(self.tasks) != tasks_completed:
            queue.extend(list(filter(lambda task: 
                             task.enter == self.time, self.tasks)))

            if not running:
                running = queue.pop(0)
                running.arrive = self.time

            running.worktime += 1
            if running.worktime == running.calc:
                tasks_completed += 1
                running.finish = self.time+1
                running = None

            self.time +=1


    def sjf(self):
        queue = []
        running: Task = None
        tasks_completed = 0
        
        get_calc = lambda task: task.calc
        while len(self.tasks) != tasks_completed:
            queue.extend(list(filter(lambda task:
                             task.enter == self.time, self.tasks)))
            queue = sorted(queue, key=get_calc)

            if not running:
                running = queue.pop(0)
                running.arrive = self.time

            running.worktime += 1
            if running.worktime == running.calc:
                tasks_completed += 1
                running.finish = self.time+1
                running = None

            self.time +=1
    
    
    def stcf(self):
        queue = []
        running: Task = None
        tasks_completed = 0
        tasks_initial = len(self.tasks)
        
        get_calc = lambda task: task.calc
        while tasks_initial != tasks_completed:
            queue.extend(list(filter(lambda task:
                             task.enter == self.time, self.tasks)))
            queue = sorted(queue, key=get_calc)
            
            if not running:
                running = queue.pop(0)
                running.arrive = self.time

            diff = running.calc-running.worktime
            if len(queue) > 0 and queue[0].calc < diff:
                running.finish = self.time
                new_task = Task(running.name, diff, 
                                running.enter, color=running.color)
                self.tasks.append(new_task)
                queue.append(new_task)
                running = queue.pop(0)
                running.arrive = self.time

            running.worktime += 1
            if running.worktime == running.calc:
                tasks_completed += 1
                running.finish = self.time+1
                running = None
            
            self.time +=1

    def rr(self):
        queue = []
        running: Task = None
        tasks_completed = 0
        tasks_initial = len(self.tasks)
        
        get_calc = lambda task: task.calc
        while tasks_initial != tasks_completed:
            queue.extend(list(filter(lambda task:
                             task.enter == self.time, self.tasks)))
            
            if not running:
                running = queue.pop(0)
                running.arrive = self.time

            running.worktime += 1
            if running.worktime == running.calc:
                tasks_completed += 1
                running.finish = self.time+1
                running = None
            else:
                running.finish = self.time
                new_task = Task(running.name, running.calc-1, 
                                running.enter, color=running.color)
                self.tasks.append(new_task)
                queue.append(new_task)
                running = queue.pop(0)
                running.arrive = self.time
                
            self.time +=1
       


def main():
    stype: SchedulerType = None
    if '--fifo' in argv: stype = SchedulerType.FIFO
    if '--sjf'  in argv: stype = SchedulerType.SJF
    if '--stcf' in argv: stype = SchedulerType.STCF
    if '--rr'   in argv: stype = SchedulerType.RR
    
    if not stype: return

    sceduler = Scheduler(stype)
    sceduler.put(Task("A", 2, 2), Task("B", 4, 0), 
                 Task("C", 2, 4), Task("D", 1, 2), 
                 Task("E", 3, 1), Task("F", 4, 0))

    sceduler.create_timeline()

    if '-t' in argv or '--timeline' in argv:
        sceduler.print_timeline()
    if '-s' in argv or '--stats' in argv:
        sceduler.print_statistics()


if __name__ == "__main__":
    main()
