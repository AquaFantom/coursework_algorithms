import random
from bisect import insort

from mimesis import Person
from mimesis.locales import Locale

person = Person(Locale.RU)

DAYS = {
    0: 'Понедельник',
    1: 'Вторник',
    2: 'Среда',
    3: 'Четверг',
    4: 'Пятница',
    5: 'Суббота',
    6: 'Воскресенье'
}
MINUTES_LIST = ['00', '15', '30', '45']
HOURS_LIST_A = ['08', '09', '10', '11', '12', '13', '14', '15', '16']
HOURS_LIST_B = ['06', '07', '08', '09', '10', '11', '12', '13', '14',
                '15', '16', '17', '18', '19', '20', '21', '22', '23', '00', '01', '02']

DRIVER_A_COST = 7000
DRIVER_B_COST = 15000
PEAK_HOURS_PROFIT = 30 * 5 * 50
NORMAL_PROFIT = 10 * 5 * 50


class Driver:
    def __init__(self, driver_type):
        self.name = person.full_name()
        self.type = driver_type
        self.trips = {
            0: [],
            1: [],
            2: [],
            3: [],
            4: [],
            5: [],
            6: []
        }

    def __str__(self):
        return f'{self.name} ({self.type})'


class Driver_A(Driver):
    def __init__(self):
        super().__init__('A')


class Driver_B(Driver):
    def __init__(self, rest_days):
        super().__init__('B')
        self.rest_days = rest_days


class Schedule:
    def __init__(self, day):
        self.day = day
        self.schedule = {}
        self.trips = []
        self.peak_trips = []
        self.drivers_a = []
        self.drivers_b = []
        self.fitness = 0

    def __str__(self):
        string = f'{DAYS.get(self.day)}\n\n'
        for trip in self.trips:
            string += f"{trip[0]} - {trip[1]}\n"
        return string

    def update_peak_trips(self):
        if self.day < 5:
            for trip in self.trips:
                if ((7 <= int(trip[0][:2]) <= 9) or (17 <= int(trip[0][:2]) <= 19)) and trip not in self.peak_trips:
                    self.peak_trips.append(trip)

    def set_fitness(self):
        self.update_peak_trips()
        profit = ((len(self.peak_trips) * PEAK_HOURS_PROFIT + (
                    len(self.trips) - len(self.peak_trips)) * NORMAL_PROFIT) -
                  (len(self.drivers_a) * DRIVER_A_COST + len(self.drivers_b) * DRIVER_B_COST))
        self.fitness = profit
        return profit


def fix_time(time):
    if time[1] == ':':
        time = '0' + time
    if time[:2] == '24':
        time = '00' + time[2:]
    if time[3:] == '60':
        time.replace(time[3:], '00')
        time = time[:3] + '00'
    return time


def is_time_overlap(trips, time_start):
    time1 = time_start
    for trip in trips:
        if time1 == trip[0]:
            return True
    return False


def is_driver_available(driver, day, time_start):
    for trip in driver.trips.get(day):
        if (abs(int(trip[0][:2] + trip[0][3:]) - int(time_start[:2] + time_start[3:])) >= 2300 or
                abs(int(trip[0][:2] + trip[0][3:]) - int(time_start[:2] + time_start[3:])) < 100):
            return False
        if int(trip[1][:2]) == int(time_start[:2]) and int(trip[1][3:]) == int(time_start[3:]):
            return False
        if int(trip[0][:2] + trip[0][3:]) == int(time_start[:2] + time_start[3:]) + 100:
            return False
    if driver.type == 'A' and not time_start[:2] in HOURS_LIST_A:
        return False
    return True

def count_weekly_profit(week):
    sum_ = 0
    for day in week:
        sum_ += day.fitness
    return sum_

def remove_trip(schedule, trip):
    schedule.trips.remove(trip)
    if trip in schedule.peak_trips:
        schedule.peak_trips.remove(trip)
    for driver in schedule.schedule:
        if trip in driver.trips[schedule.day]:
            driver.trips[schedule.day].remove(trip)
        if trip in schedule.schedule[driver]:
            schedule.schedule[driver].remove(trip)


def add_trip(schedule, driver, time_start, time_end):
    insort(driver.trips.get(schedule.day), (time_start, time_end), key=lambda x: int(x[0][:2] + x[0][3:]))
    insort(schedule.trips, (time_start, time_end), key=lambda x: int(x[0][:2] + x[0][3:]))
    if driver not in schedule.schedule:
        schedule.schedule[driver] = []
    insort(schedule.schedule[driver], (time_start, time_end), key=lambda x: int(x[0][:2] + x[0][3:]))



def create_trip(driver, schedule):
    driver.trips.get(schedule.day).sort(key=lambda x: int(x[0][:2] + x[0][3:]))
    time_start = None
    for _ in range(20):
        if driver.type == 'A':
            if schedule.day < 5:
                hour_index = random.choice([0, 1]) if random.random() < 0.7 else random.randint(2, len(HOURS_LIST_A) - 1)
            else:
                hour_index = random.randint(0, len(HOURS_LIST_A) - 1)
            time_start = HOURS_LIST_A[hour_index] + ':' + random.choice(MINUTES_LIST)
        else:
            if schedule.day < 5:
                hour_index = random.choice([1, 2, 3, 11, 12, 13]) if random.random() < 0.7 else random.choice([0, 4, 5, 6, 7, 8, 9, 10, 14, 15, 16, 17, 18, 19, 20])
            else:
                hour_index = random.randint(0, len(HOURS_LIST_B) - 1)
            time_start = HOURS_LIST_B[hour_index] + ':' + random.choice(MINUTES_LIST)
        if not is_driver_available(driver, schedule.day, time_start):
            time_start = None
            continue
        if is_time_overlap(schedule.trips, time_start):
            time_start = None
            continue
        break

    if time_start is None:
        return
    time_end = str(int(time_start[:2]) + 1) + ':' + time_start[3:]
    time_end = fix_time(time_end)
    if driver.type == 'A':
        if driver not in schedule.drivers_a:
            schedule.drivers_a.append(driver)
    else:
        if driver not in schedule.drivers_b:
            schedule.drivers_b.append(driver)
    add_trip(schedule, driver, time_start, time_end)


def create_daily_schedule(day, drivers_a, drivers_b):
    schedule = Schedule(day)
    num = random.randint(len(drivers_a) + len(drivers_b), 88)
    for _ in range(num):
        driver_type = random.choice(['A', 'B'])
        if driver_type == 'A' and day < 5 and drivers_a:
            driver = random.choice(drivers_a)
            create_trip(driver, schedule)
        elif drivers_b:
            driver = random.choice(drivers_b)
            create_trip(driver, schedule)
    if day < 5:
        schedule.update_peak_trips()

    first_trip = False
    last_trip = False
    for trip in schedule.trips:
        if trip[0][:2] == '06':
            first_trip = True
        if trip[0][:2] == '02' or trip[0][:2] == '03':
            last_trip = True
    if not first_trip:
        for driver in schedule.drivers_b:
            if is_driver_available(driver, schedule.day, '06:00'):
                add_trip(schedule, driver, '06:00', '07:00')
                break
    if not last_trip:
        for driver in schedule.drivers_b:
            if is_driver_available(driver, schedule.day, '02:00'):
                add_trip(schedule, driver, '02:00', '03:00')
                break
    schedule.set_fitness()
    return schedule


def create_weekly_schedule(all_drivers_a, all_drivers_b):
    week_schedule = []
    drivers_a = all_drivers_a.copy()
    for day in range(7):
        drivers_b = []
        for driver in all_drivers_b:
            if driver.rest_days == 0:
                drivers_b.append(driver)
            elif driver.rest_days == 3:
                drivers_b.append(driver)
                driver.rest_days = 0
            driver.rest_days += 1
        if not drivers_b:
            new_b = Driver_B(1)
            drivers_b.append(new_b)
            all_drivers_b.append(new_b)
        week_schedule.append(create_daily_schedule(day, drivers_a, drivers_b))

    return week_schedule


def create_drivers():
    drivers_a = []
    drivers_b = []
    drivers_amount = random.randint(2, 5)
    for _ in range(drivers_amount):
        driver_type = random.choice(['A', 'B'])
        if driver_type == 'A':
            drivers_a.append(Driver_A())
        else:
            drivers_b.append(Driver_B(random.randint(0, 2)))
    return drivers_a, drivers_b
