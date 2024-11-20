from sys import argv
from time import sleep
from rich.console import Console
from random import randint
    
class SchedulerType():
    FIFO = "FIFO (First In First Out)"
    SJF  = "SJF (Shortest Job First)"
    STCF = "STCF (Shortest Time to Completion First)"
    RR   = "RR (Round Robin)"

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
        self.slicetask: Task = None

        if color == "none": 
            self.color = colors[randint(0, len(colors)-1)]
            colors.remove(self.color)
        else: self.color = color
    
    def pass_time(self):
        return self.finish-self.enter

    def answer_time(self):
        return self.arrive-self.enter
    
    def __str__(self):
        return (f"{self.name}:  WORKT_EST={self.calc:2}  SCHEDULED_AT={self.enter:2}  FIRST_ENTRY={self.arrive:2}  FINISHED_AT={self.finish:2}" +
                f"\n    PASS_TIME={self.pass_time():2} ({self.finish}-{self.enter})" +
                f"\n    ANSWER_TIME={self.answer_time():2} ({self.arrive}-{self.enter})  SLICED={self.slicetask!=None}\n")

class Scheduler():
    def __init__(self, type: SchedulerType):
        self.tasks = []
        self.timeline = []
        self._type = type
        self.time = 0
    

    def put(self, *tasks: Task):
        for task in tasks:
            self.tasks.append(task)


    def create_timeline(self):
        self.timeline = self.tasks.copy()
        match self._type:
            case SchedulerType.FIFO: self.fifo()
            case SchedulerType.SJF:  self.sjf()
            case SchedulerType.STCF: self.stcf()
            case SchedulerType.RR:   self.rr()
    
    def print_timeline(self):
        get_arrive = lambda task: task.arrive
        console.print()
        for task in sorted(self.timeline, key=get_arrive):
            length = int((task.worktime*6-1))
            console.print('┃' + length*'░', end='', style=task.color)
        console.print('┃')
        for task in sorted(self.timeline, key=get_arrive):
            length = int((task.worktime*6-1)/2)-1
            console.print('┃' + length*'░' + f'▏{task.name}▕' + length*'░', end='', style=task.color)
        console.print('┃')
        for task in sorted(self.timeline, key=get_arrive):
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

        for task in self.tasks:
            last_slice = task
            while last_slice.slicetask != None:
                last_slice = last_slice.slicetask
            task.finish = last_slice.finish
            task.worktime = task.calc

        get_arrive = lambda task: task.arrive
        for task in sorted(self.tasks, key=get_arrive): print(task)
        print(f"PASS_TIME_AVG={sum(list(map(lambda task: task.pass_time(), self.tasks)))/len(self.tasks):2.2f}")
        print(f"ANSWER_TIME_AVG={sum(list(map(lambda task: task.answer_time(), self.tasks)))/len(self.tasks):2.2f}")
        print() 


    def fifo(self):
        queue = []
        running: Task = None
        tasks_completed = 0

        while len(self.timeline) != tasks_completed:
            queue.extend(list(filter(lambda task: 
                             task.enter == self.time, self.timeline)))

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
        while len(self.timeline) != tasks_completed:
            queue.extend(list(filter(lambda task:
                             task.enter == self.time, self.timeline)))
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
        tasks_initial = len(self.timeline)
        
        get_calc = lambda task: task.calc
        while tasks_initial != tasks_completed:
            queue.extend(list(filter(lambda task:
                             task.enter == self.time, self.timeline)))
            queue = sorted(queue, key=get_calc)
            
            if not running:
                running = queue.pop(0)
                running.arrive = self.time

            diff = running.calc-running.worktime
            if len(queue) > 0 and queue[0].calc < diff:
                running.finish = self.time
                new_task = Task(running.name, diff, 
                                running.enter, color=running.color)
                self.timeline.append(new_task)
                queue.append(new_task)
                running.slicetask = new_task
                
                running = queue.pop(0)
                running.arrive = self.time

            running.worktime += 1
            self.time +=1
            if running.worktime == running.calc:
                tasks_completed += 1
                running.finish = self.time
                running = None

    def rr(self):
        queue = []
        running: Task = None
        tasks_completed = 0
        tasks_initial = len(self.timeline)
        
        get_calc = lambda task: task.calc
        while tasks_initial != tasks_completed:
            
            queue.extend(list(filter(lambda task:
                             task.enter == self.time, self.timeline)))
            for task in queue:
                print(f"{task.name} ", end ='')
            print()
            if not running:
                running = queue.pop(0)
                running.arrive = self.time

            running.worktime += 1
            self.time +=1
            if running.worktime == running.calc:
                tasks_completed += 1
                running.finish = self.time
                running = None
            else:
                running.finish = self.time
                new_task = Task(running.name, running.calc-1, 
                                running.enter, color=running.color)
                self.timeline.append(new_task)
                queue.append(new_task)
                running.slicetask = new_task

                running = queue.pop(0)
                running.arrive = self.time 


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
