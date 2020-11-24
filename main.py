from src.sea_channel import SeaChannelEventsLoopHandler


if __name__ == "__main__":
    sea_channel = SeaChannelEventsLoopHandler()
    for event in sea_channel.event_loop():
        print(event)
        pass

    total_awaited = sum(ship.waiting_time for ship in sea_channel.ships_exited)
    ships_exited = sea_channel.ships_exited.copy()

    print('-' * 70)

    while any(ships_exited):
        chunk = ships_exited[:2]
        ships_exited = ships_exited[2:]
        if chunk:
            # print(chunk)
            print('  |  '.join(str(s) for s in chunk), ' |')

    print('-' * 70)

    print('Total    Ships:', len(sea_channel.ships_exited))
    print('Total  Awaited:', total_awaited)
    print('Median Awaited:', total_awaited / len(sea_channel.ships_exited))
    print('-' * 70)
