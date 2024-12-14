from initial import *


def cross_trip(trip, child1, child2):
    if is_time_overlap(child2.trips, trip[0]):
        return
    remove_trip(child1, trip)
    for driver in child2.drivers_a:
        if is_driver_available(driver, child2.day, trip[0]):
            add_trip(child2, driver, trip[0], trip[1])
            return
    for driver in child2.drivers_b:
        if is_driver_available(driver, child2.day, trip[0]):
            add_trip(child2, driver, trip[0], trip[1])
            return
    new_driver = Driver_A() if trip[0][:2] in HOURS_LIST_A else Driver_B(1)
    add_trip(child2, new_driver, trip[0], trip[1])
    if new_driver.type == 'A':
        child2.drivers_a.append(new_driver)
    else:
        child2.drivers_b.append(new_driver)


def crossover(child1, child2):
    s = random.randint(2, min(len(child1.trips), len(child2.trips)) // 2 + 1)
    trips_1 = child1.trips[::s]
    trips_2 = child2.trips[::s]

    for trip in trips_1:
        cross_trip(trip, child1, child2)

    for trip in trips_2:
        cross_trip(trip, child2, child1)

    child1.set_fitness()
    child2.set_fitness()


def add_mutant_trip(mutant, time_start, time_end):
    for driver in mutant.drivers_a:
        if is_driver_available(driver, mutant.day, time_start):
            add_trip(mutant, driver, time_start, time_end)
            return True
    for driver in mutant.drivers_b:
        if is_driver_available(driver, mutant.day, time_start):
            add_trip(mutant, driver, time_start, time_end)
            return True
    return False


def mutate(mutant, indpb=0.01):
    for i in range(len(mutant.trips)):
        if random.random() < indpb:
            time_start = random.choice(HOURS_LIST_B) + ':' + random.choice(MINUTES_LIST)
            time_end = str(int(time_start[:2]) + 1) + ':' + time_start[3:]
            time_end = fix_time(time_end)
            trip = (time_start, time_end)
            if trip in mutant.trips:
                remove_trip(mutant, trip)
                continue
            if add_mutant_trip(mutant, time_start, time_end):
                continue
            new_driver = Driver_A() if time_start[:2] in HOURS_LIST_A else Driver_B(1)
            add_trip(mutant, new_driver, time_start, time_end)
            if new_driver.type == 'A':
                mutant.drivers_a.append(new_driver)
            else:
                mutant.drivers_b.append(new_driver)


def remove_empty_drivers(day):
    for driver in day.drivers_a:
        if not day.schedule.get(driver):
            day.drivers_a.remove(driver)
            day.schedule.pop(driver)
    for driver in day.drivers_b:
        if not day.schedule.get(driver):
            day.drivers_b.remove(driver)
            day.schedule.pop(driver)
            driver.rest_day = 0


def gen_algorithm(gens_max, p_crossover=0.9, p_mutation=0.5):
    drivers_a, drivers_b = create_drivers()
    population = create_weekly_schedule(drivers_a, drivers_b)
    gen_counter = 0

    while gen_counter < gens_max:
        gen_counter += 1
        offspring = population

        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < p_crossover and child1.day != child2.day:
                crossover(child1, child2)

        for mutant in offspring:
            if random.random() < p_mutation:
                mutate(mutant, indpb=1.0/len(mutant.trips))

        new_fitness_values = [individual.set_fitness() for individual in offspring]
        for individual, fitness_value in zip(offspring, new_fitness_values):
            individual.fitness = fitness_value

        population[:] = offspring

    for day in population:
        remove_empty_drivers(day)

    for day in population:
        day.set_fitness()

    return population
