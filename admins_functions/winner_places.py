from get_bot_and_db import get_bot_and_db


def winner_places(code, text=None, winner=None, admin=None):
    bot, db = get_bot_and_db()
    users = db.get_bid(code)
    max_bids = list()
    usernames = list()

    # print(f"{users =}")
    if len(users) > 0:
        for num in range(-100, 0, -1):
            try:
                if users[num][1] == users[num - 1][1]:
                    users.remove(users[-2])
            except IndexError:
                continue

        if len(users) > 0:
            for _ in range(4):
                try:
                    maximum = max(users, key=lambda x: x[2])[1]
                except ValueError:
                    break

                # print(f"{maximum = } {usernames = }")
                if maximum not in usernames:
                    usernames.append(maximum)
                    max_bids.append(max(users, key=lambda x: x[2]))
                    for e in users:
                        # print("eee", e[1], maximum, users)
                        if e[1] == maximum:
                            users.remove(e)

        # print(f"{usernames =}, {max_bids =}")
        # print(sorted(max_bids, key=lambda x: x[2], reverse=True))
        winners = sorted(max_bids, key=lambda x: x[2], reverse=True)
        # print(f"{winners =}")
        if winner:
            first_place = list(winners[0][1])
            for num in range(1, len(first_place) - 1):
                first_place[-num] = "*"
            first_place = "".join(first_place)

            winner_text = f"🥇 {first_place} {winners[0][2]}\n"

            return winner_text

        elif text:
            if len(winners) == 3:
                if admin:
                    winner_text = f"🥇 {winners[0][1]} {winners[0][2]}\n" \
                                  f"🥈 {winners[1][1]} {winners[1][2]}\n" \
                                  f"🥉 {winners[2][1]} {winners[2][2]}\n"

                    return winner_text
                else:
                    first_place = list(winners[0][1])
                    for num in range(1, len(first_place) - 1):
                        first_place[-num] = "*"
                    first_place = "".join(first_place)

                    second_place = list(winners[1][1])
                    for num in range(1, len(second_place) - 1):
                        second_place[-num] = "*"
                    second_place = "".join(second_place)

                    third_place = list(winners[2][1])
                    for num in range(1, len(third_place) - 1):
                        third_place[-num] = "*"
                    third_place = "".join(third_place)

                    winner_text = f"🥇 {first_place} {winners[0][2]}\n" \
                                   f"🥈 {second_place} {winners[1][2]}\n" \
                                   f"🥉 {third_place} {winners[2][2]}\n"

                    return winner_text

            elif len(winners) == 2:
                if admin:
                    winner_text = f"🥇 {winners[0][1]} {winners[0][2]}\n" \
                                  f"🥈 {winners[1][1]} {winners[1][2]}\n" \

                    return winner_text

                else:
                    first_place = list(winners[0][1])
                    for num in range(1, len(first_place) - 1):
                        first_place[-num] = "*"
                    first_place = "".join(first_place)

                    second_place = list(winners[1][1])
                    for num in range(1, len(second_place) - 1):
                        second_place[-num] = "*"
                    second_place = "".join(second_place)

                    winner_text = f"🥇 {first_place} {winners[0][2]}\n" \
                                   f"🥈 {second_place} {winners[1][2]}\n"

                    return winner_text

            elif len(winners) == 1:
                if admin:
                    winner_text = f"🥇 {winners[0][1]} {winners[0][2]}\n"
                    return winner_text

                else:
                    first_place = list(winners[0][1])
                    for num in range(1, len(first_place) - 1):
                        first_place[-num] = "*"
                    first_place = "".join(first_place)

                    winner_text = f"🥇 {first_place} {winners[0][2]}\n"

                    return winner_text

            else:
                return None

        return winners
    return ""