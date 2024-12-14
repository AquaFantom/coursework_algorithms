from initial import *


def create_drivers_brut(drivers_a_amount, drivers_b_amount):
    drivers_a = []
    drivers_b = []
    for _ in range(drivers_a_amount):
        drivers_a.append(Driver_A())
    for _ in range(drivers_b_amount):
        drivers_b.append(Driver_B(random.randint(0, 2)))
    return drivers_a, drivers_b


def calculate_best_schedule():
    best_schedule = None
    best_fitness = 0
    for i in range(44):
        for j in range(44):
            drivers_a, drivers_b = create_drivers_brut(i, j)
            week_schedule = create_weekly_schedule(drivers_a, drivers_b)
            fitness = count_weekly_profit(week_schedule)
            if fitness >= best_fitness:
                best_fitness = fitness
                best_schedule = week_schedule
    return best_schedule