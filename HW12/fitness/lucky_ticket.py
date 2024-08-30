import multiprocessing
from itertools import product


def is_happy(ticket):
    first_half = sum(int(digit) for digit in ticket[:3])
    second_half = sum(int(digit) for digit in ticket[3:])
    return first_half == second_half


def count_happy_tickets(start, end):
    count = 0
    for ticket in range(start, end):
        ticket_str = str(ticket).zfill(6)
        if is_happy(ticket_str):
            count += 1
    return count


def parallel_count_happy_tickets(num_processes):
    total_tickets = 10 ** 6
    chunk_size = total_tickets // num_processes

    with multiprocessing.Pool(num_processes) as pool:
        results = [
            pool.apply_async(count_happy_tickets, (i * chunk_size, (i + 1) * chunk_size))
            for i in range(num_processes)
        ]
        happy_count = sum(result.get() for result in results)
    return happy_count


if __name__ == "__main__":
    num_processes = 4
    happy_tickets_count = parallel_count_happy_tickets(num_processes)
    print(f"Happy tickets count: {happy_tickets_count}")
